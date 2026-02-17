"""
Team Members API Routes

Routes are protected with RBAC (Role-Based Access Control).
"""
from flask import Blueprint, request, g
from app.services import TeamService
from app.utils import (
    api_response,
    paginated_response,
    error_response,
    validate_json,
    validate_required_fields,
    validate_pagination
)
from app.utils.rbac import (
    require_auth,
    require_permission,
    require_manager,
    Permission
)

team_bp = Blueprint('team', __name__, url_prefix='/api/team')


@team_bp.route('', methods=['GET'])
@require_auth
@validate_pagination
def get_team_members():
    """
    Get all team members (requires authentication)

    Query params:
        - department: Filter by department
        - status: Filter by status (active, away, offline)
        - page: Page number (default: 1)
        - limit: Items per page (default: 50, max: 100)

    Response: PaginatedResponse<TeamMember[]>
    """
    department = request.args.get('department')
    status = request.args.get('status')
    page = request.pagination['page']
    limit = request.pagination['limit']

    team_members, total = TeamService.get_all(
        department=department,
        status=status,
        page=page,
        limit=limit
    )

    return paginated_response(
        data=[m.to_dict() for m in team_members],
        page=page,
        limit=limit,
        total=total
    )


@team_bp.route('/<team_member_id>', methods=['GET'])
@require_auth
def get_team_member(team_member_id):
    """
    Get a single team member by ID (requires authentication)

    Response: ApiResponse<TeamMember>
    """
    team_member = TeamService.get_by_id(team_member_id)

    if not team_member:
        return error_response('Team member not found', 404)

    return api_response(data=team_member.to_dict())


@team_bp.route('', methods=['POST'])
@require_permission(Permission.MANAGE_TEAM)
@validate_json
@validate_required_fields(['name', 'email', 'role'])
def create_team_member():
    """
    Create a new team member (Manager+ only)

    Body (CreateTeamMemberInput):
        - name: string (required)
        - email: string (required)
        - role: string (required)
        - department: string
        - status: 'active' | 'away' | 'offline'

    Response: ApiResponse<TeamMember>
    """
    data = request.get_json()

    # Check if email already exists
    existing = TeamService.get_by_email(data['email'])
    if existing:
        return error_response('A team member with this email already exists', 409)

    try:
        team_member = TeamService.create(data)
        return api_response(
            data=team_member.to_dict(),
            message='Team member created successfully',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to create team member: {str(e)}', 500)


@team_bp.route('/<team_member_id>', methods=['PUT'])
@require_permission(Permission.MANAGE_TEAM)
@validate_json
def update_team_member(team_member_id):
    """
    Update an existing team member (Manager+ only)

    Body (UpdateTeamMemberInput):
        - name: string
        - email: string
        - role: string
        - department: string
        - status: 'active' | 'away' | 'offline'

    Response: ApiResponse<TeamMember>
    """
    data = request.get_json()

    # Check if email is being changed to one that already exists
    if 'email' in data:
        existing = TeamService.get_by_email(data['email'])
        if existing and existing.id != team_member_id:
            return error_response('A team member with this email already exists', 409)

    try:
        team_member = TeamService.update(team_member_id, data)

        if not team_member:
            return error_response('Team member not found', 404)

        return api_response(
            data=team_member.to_dict(),
            message='Team member updated successfully'
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to update team member: {str(e)}', 500)


@team_bp.route('/<team_member_id>', methods=['DELETE'])
@require_permission(Permission.MANAGE_TEAM)
def delete_team_member(team_member_id):
    """
    Delete a team member (Manager+ only)

    Response: ApiResponse<null>
    """
    success = TeamService.delete(team_member_id)

    if not success:
        return error_response('Team member not found', 404)

    return api_response(
        data=None,
        message='Team member deleted successfully'
    )


@team_bp.route('/<team_member_id>/status', methods=['PATCH'])
@require_permission(Permission.MANAGE_TEAM)
@validate_json
@validate_required_fields(['status'])
def update_team_member_status(team_member_id):
    """
    Quick update team member status (Manager+ only)

    Body:
        - status: 'active' | 'away' | 'offline' (required)

    Response: ApiResponse<TeamMember>
    """
    data = request.get_json()
    status = data['status']

    valid_statuses = ['active', 'away', 'offline']
    if status not in valid_statuses:
        return error_response(f'Invalid status. Allowed: {", ".join(valid_statuses)}', 400)

    team_member = TeamService.update_status(team_member_id, status)

    if not team_member:
        return error_response('Team member not found', 404)

    return api_response(
        data=team_member.to_dict(),
        message='Team member status updated'
    )


@team_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """
    Get list of all departments (requires authentication)

    Response: ApiResponse<string[]>
    """
    departments = TeamService.get_departments()
    return api_response(data=departments)
