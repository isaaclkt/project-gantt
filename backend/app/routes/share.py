"""
Share Links API Routes

Routes for managing project share links (temporary public access).
"""
from flask import Blueprint, request, g
from flask_jwt_extended import get_jwt_identity
from app.services import ShareLinkService
from app.models import ShareLink
from app.utils import api_response, error_response, validate_json
from app.utils.rbac import require_auth, require_project_access, has_role, Role

share_bp = Blueprint('share', __name__, url_prefix='/api/share')


@share_bp.route('/projects/<project_id>', methods=['POST'])
@require_project_access(allow_owner=True, allow_member=False, allow_manager=True)
@validate_json
def create_share_link(project_id):
    """
    Create a share link for a project (Owner or Manager+ only)

    Body:
        - expiresInDays: number (optional, default 7, max 30)

    Response: ApiResponse<ShareLink>
    """
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    expires_in_days = data.get('expiresInDays', 7)

    # Validate expiry
    if not isinstance(expires_in_days, int) or expires_in_days < 1 or expires_in_days > 30:
        return error_response('expiresInDays deve ser entre 1 e 30', 400)

    try:
        share_link = ShareLinkService.create(
            project_id=project_id,
            created_by=user_id,
            expires_in_days=expires_in_days
        )
        return api_response(
            data=share_link.to_dict(),
            message='Link de compartilhamento criado com sucesso',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f'Erro ao criar link de compartilhamento: {str(e)}', 500)


@share_bp.route('/projects/<project_id>/links', methods=['GET'])
@require_project_access(allow_owner=True, allow_member=False, allow_manager=True)
def get_project_share_links(project_id):
    """
    Get all share links for a project (Owner or Manager+ only)

    Response: ApiResponse<ShareLink[]>
    """
    links = ShareLinkService.get_by_project(project_id)
    return api_response(data=[link.to_dict() for link in links])


@share_bp.route('/links/<link_id>', methods=['DELETE'])
@require_auth
def revoke_share_link(link_id):
    """
    Revoke a share link (Creator or Admin only)
    Note: This is a soft delete - the link is not physically deleted

    Response: ApiResponse<null>
    """
    share_link = ShareLinkService.get_by_id(link_id)

    if not share_link:
        return error_response('Link de compartilhamento não encontrado', 404)

    user_id = get_jwt_identity()
    user_role = g.current_user.role

    # Only creator or admin can revoke
    if share_link.created_by != user_id and not has_role(user_role, Role.ADMIN.value):
        return error_response('Acesso negado', 403)

    ShareLinkService.revoke(link_id)
    return api_response(data=None, message='Link de compartilhamento revogado com sucesso')


# ============================================
# PUBLIC ROUTES (No auth required)
# ============================================

@share_bp.route('/public/<token>', methods=['GET'])
def get_shared_project(token):
    """
    Get project data via share token (PUBLIC - no auth required)
    Records access metrics on successful access

    Response: ApiResponse<ProjectWithTasks>
    """
    share_link = ShareLinkService.get_valid_by_token(token)

    if not share_link:
        return error_response('Link inválido ou expirado', 404)

    project = share_link.project
    if not project or project.is_deleted:
        return error_response('Projeto não encontrado', 404)

    # Record access metrics (non-blocking - failure won't affect response)
    ShareLinkService.record_access(token)

    # Return project with tasks for Gantt visualization
    project_data = project.to_dict_with_tasks()

    # Add team members info for display (limited info for public view)
    team_members = []
    for member in project.team_members:
        team_members.append({
            'id': member.id,
            'name': member.name,
            'avatar': member.avatar,
            'role': member.role
        })
    project_data['teamMembers'] = team_members

    return api_response(data=project_data)
