"""
Invites API Routes

Routes for managing team member invitations.
"""
from flask import Blueprint, request, g
from flask_jwt_extended import get_jwt_identity
from app.services import InviteService, AuditService
from app.models import User
from app.utils import (
    api_response,
    paginated_response,
    error_response,
    validate_json,
    validate_required_fields,
    validate_string_length
)
from app.utils.rbac import (
    require_auth,
    require_role,
    require_permission,
    Permission,
    Role,
    has_role
)

invites_bp = Blueprint('invites', __name__, url_prefix='/api/invites')


@invites_bp.route('', methods=['POST'])
@require_auth
@validate_json
@validate_required_fields(['email', 'role'])
@validate_string_length('email', max_length=255)
def create_invite():
    """
    Create a new team member invite (Manager+ only)

    Rules:
    - Department admins can only invite to their own department
    - Cannot invite users as department_admin
    - Role must be: manager, member, or viewer

    Body:
        - email: string (required)
        - role: 'manager' | 'member' | 'viewer' (required)
        - departmentId: string (optional, defaults to creator's department)
        - password: string (optional, pre-set password for the invitee)
        - expiresInDays: number (optional, default 7, max 30)

    Response: ApiResponse<Invite>
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    # Check permissions
    user = User.query.get(user_id)
    if not user:
        return error_response('User not found', 404)

    user_role = user.role or Role.MEMBER.value

    # Only manager+ can create invites
    if not has_role(user_role, Role.MANAGER.value):
        return error_response('Permissão negada. Apenas gerentes podem criar convites.', 403)

    email = data.get('email', '').lower()
    role = data.get('role')
    department_id = data.get('departmentId')
    password = data.get('password')
    expires_in_days = data.get('expiresInDays', 7)

    # Validate expiry
    if not isinstance(expires_in_days, int) or expires_in_days < 1 or expires_in_days > 30:
        return error_response('expiresInDays deve ser entre 1 e 30', 400)

    try:
        invite = InviteService.create(
            email=email,
            role=role,
            created_by=user_id,
            department_id=department_id,
            password=password,
            expires_in_days=expires_in_days
        )

        # Log the invite creation
        AuditService.log_invite_created(
            invite_id=invite.id,
            email=email,
            role=role,
            department_id=invite.department_id
        )

        return api_response(
            data=invite.to_dict(),
            message='Convite criado com sucesso',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Erro ao criar convite: {str(e)}', 500)


@invites_bp.route('/<token>/accept', methods=['POST'])
@validate_json
def accept_invite(token):
    """
    Accept an invite and create a new user (PUBLIC - no auth required)
    The invite token must be valid (not expired, used, or revoked)

    Body:
        - password: string (required unless pre-set password exists)

    Response: ApiResponse<User>
    """
    data = request.get_json()
    password = data.get('password')

    try:
        invite = InviteService.get_valid_by_token(token)
        if not invite:
            return error_response('Convite inválido, expirado ou revogado', 404)

        user = InviteService.accept(token, password)

        # Log the invite acceptance
        AuditService.log_invite_accepted(
            invite_id=invite.id,
            user_id=user.id,
            email=invite.email
        )

        return api_response(
            data=user.to_dict(),
            message='Conta criada com sucesso! Você pode fazer login.',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Erro ao aceitar convite: {str(e)}', 500)


@invites_bp.route('/<invite_id>', methods=['DELETE'])
@require_auth
def revoke_invite(invite_id):
    """
    Revoke an invite (Creator or Admin only)
    Note: This is a soft delete - the invite is not physically deleted

    Response: ApiResponse<null>
    """
    invite = InviteService.get_by_id(invite_id)

    if not invite:
        return error_response('Convite não encontrado', 404)

    user_id = get_jwt_identity()
    user_role = g.current_user.role

    # Only creator or admin can revoke
    if invite.created_by != user_id and not has_role(user_role, Role.ADMIN.value):
        return error_response('Acesso negado', 403)

    InviteService.revoke(invite_id)

    # Log the revocation
    AuditService.log_invite_revoked(
        invite_id=invite_id,
        email=invite.email
    )

    return api_response(data=None, message='Convite revogado com sucesso')


@invites_bp.route('', methods=['GET'])
@require_auth
def get_invites():
    """
    Get invites based on user role (Manager+ only)

    - Admin: All invites
    - Department Admin: Invites for their department only
    - Manager: Invites they created

    Query params:
        - departmentId: Filter by department (admin/department_admin only)

    Response: ApiResponse<Invite[]>
    """
    user_id = get_jwt_identity()
    user = g.current_user
    user_role = user.role or Role.MEMBER.value

    # Only manager+ can view invites
    if not has_role(user_role, Role.MANAGER.value):
        return error_response('Permissão negada', 403)

    department_id = request.args.get('departmentId')

    if has_role(user_role, Role.ADMIN.value):
        # Admin can see all invites, optionally filtered by department
        if department_id:
            invites = InviteService.get_by_department(department_id)
        else:
            invites = Invite.query.order_by(Invite.created_at.desc()).all()
    elif user_role == Role.DEPARTMENT_ADMIN.value:
        # Department admin can only see their department's invites
        if department_id and department_id != user.department_id:
            return error_response('Você só pode ver convites do seu departamento', 403)
        invites = InviteService.get_by_department(user.department_id)
    else:
        # Managers can only see invites they created
        invites = InviteService.get_by_creator(user_id)

    return api_response(data=[invite.to_dict() for invite in invites])


@invites_bp.route('/<invite_id>', methods=['GET'])
@require_auth
def get_invite(invite_id):
    """
    Get a single invite by ID (Creator, Admin, or Department Admin of same dept)

    Response: ApiResponse<Invite>
    """
    invite = InviteService.get_by_id(invite_id)

    if not invite:
        return error_response('Convite não encontrado', 404)

    user_id = get_jwt_identity()
    user = g.current_user
    user_role = user.role or Role.MEMBER.value

    # Check access
    can_access = (
        has_role(user_role, Role.ADMIN.value) or
        invite.created_by == user_id or
        (user_role == Role.DEPARTMENT_ADMIN.value and invite.department_id == user.department_id)
    )

    if not can_access:
        return error_response('Acesso negado', 403)

    return api_response(data=invite.to_dict())


@invites_bp.route('/validate/<token>', methods=['GET'])
def validate_invite(token):
    """
    Validate an invite token (PUBLIC - no auth required)

    Checks if the invite is valid (not expired, used, or revoked)

    Response: ApiResponse<InviteInfo>
    """
    invite = InviteService.get_valid_by_token(token)

    if not invite:
        return error_response('Convite inválido ou expirado', 404)

    # Return limited info for validation
    return api_response(data={
        'email': invite.email,
        'role': invite.role,
        'departmentName': invite.department.name if invite.department else None,
        'hasPassword': invite.password is not None
    })
