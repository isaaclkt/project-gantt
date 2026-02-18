"""
Projects API Routes

Routes are protected with RBAC (Role-Based Access Control).
"""
from flask import Blueprint, request, g
from flask_jwt_extended import get_jwt_identity
from app.services import ProjectService
from app.utils import (
    api_response,
    paginated_response,
    error_response,
    validate_json,
    validate_required_fields,
    validate_pagination,
    validate_date_range,
    validate_progress,
    validate_string_length,
    validate_enum_field
)
from app.utils.rbac import (
    require_auth,
    require_permission,
    require_project_access,
    require_project_department_scope,
    Permission,
    Role,
    has_role,
    is_project_owner
)

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['GET'])
@require_auth
@validate_pagination
def get_projects():
    """
    Get all projects (requires authentication)

    Query params:
        - status: Filter by status (planning, active, on-hold, completed)
        - page: Page number (default: 1)
        - limit: Items per page (default: 10, max: 100)

    Response: PaginatedResponse<Project[]>
    """
    status = request.args.get('status')
    page = request.pagination['page']
    limit = request.pagination['limit']

    projects, total = ProjectService.get_all(status=status, page=page, limit=limit)

    return paginated_response(
        data=[p.to_dict() for p in projects],
        page=page,
        limit=limit,
        total=total
    )


@projects_bp.route('/<project_id>', methods=['GET'])
@require_auth
@require_project_department_scope
def get_project(project_id):
    """
    Get a single project by ID (requires authentication)
    Department admins can only access projects in their department.

    Response: ApiResponse<Project>
    """
    project = ProjectService.get_by_id(project_id)

    if not project:
        return error_response('Project not found', 404)

    return api_response(data=project.to_dict())


@projects_bp.route('', methods=['POST'])
@require_permission(Permission.CREATE_PROJECTS)
@validate_json
@validate_required_fields(['name', 'startDate', 'endDate'])
@validate_string_length('name', min_length=1, max_length=255)
@validate_date_range('startDate', 'endDate')
@validate_enum_field('status', ['planning', 'active', 'on-hold', 'completed'])
def create_project():
    """
    Create a new project (requires CREATE_PROJECTS permission - Manager+)

    Body (CreateProjectInput):
        - name: string (required)
        - description: string
        - color: string (hex color)
        - status: 'planning' | 'active' | 'on-hold' | 'completed'
        - startDate: string (YYYY-MM-DD, required)
        - endDate: string (YYYY-MM-DD, required)
        - teamMemberIds: string[]

    Response: ApiResponse<Project>
    """
    data = request.get_json()

    # Set the owner to current user
    data['ownerId'] = get_jwt_identity()

    try:
        project = ProjectService.create(data)
        return api_response(
            data=project.to_dict(),
            message='Project created successfully',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to create project: {str(e)}', 500)


@projects_bp.route('/<project_id>', methods=['PUT'])
@require_project_access(allow_owner=True, allow_member=False, allow_manager=True)
@validate_json
@validate_string_length('name', min_length=1, max_length=255)
@validate_date_range('startDate', 'endDate')
@validate_progress('progress')
@validate_enum_field('status', ['planning', 'active', 'on-hold', 'completed'])
def update_project(project_id):
    """
    Update an existing project (Owner or Manager+ only)

    Body (UpdateProjectInput):
        - name: string
        - description: string
        - color: string
        - status: string
        - progress: number (0-100)
        - startDate: string (YYYY-MM-DD)
        - endDate: string (YYYY-MM-DD)
        - teamMemberIds: string[]

    Response: ApiResponse<Project>
    """
    data = request.get_json()

    try:
        project = ProjectService.update(project_id, data)

        if not project:
            return error_response('Project not found', 404)

        return api_response(
            data=project.to_dict(),
            message='Project updated successfully'
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to update project: {str(e)}', 500)


@projects_bp.route('/<project_id>', methods=['DELETE'])
@require_permission(Permission.DELETE_PROJECTS)
def delete_project(project_id):
    """
    Delete a project (Admin only)

    Response: ApiResponse<null>
    """
    try:
        success = ProjectService.delete(project_id)

        if not success:
            return error_response('Project not found', 404)

        return api_response(
            data=None,
            message='Project deleted successfully'
        )
    except Exception as e:
        return error_response(f'Failed to delete project: {str(e)}', 500)


@projects_bp.route('/<project_id>/tasks', methods=['GET'])
@require_auth
@require_project_department_scope
def get_project_tasks(project_id):
    """
    Get all tasks for a specific project (requires authentication)
    Department admins can only access tasks from projects in their department.

    Response: ApiResponse<Task[]>
    """
    project = ProjectService.get_by_id(project_id)

    if not project:
        return error_response('Project not found', 404)

    tasks = ProjectService.get_project_tasks(project_id)

    return api_response(data=[t.to_dict() for t in tasks])


@projects_bp.route('/<project_id>/members', methods=['GET'])
@require_auth
@require_project_department_scope
def get_project_members(project_id):
    """
    Get all team members of a project (requires authentication)
    Department admins can only access members of projects in their department.

    Response: ApiResponse<TeamMember[]>
    """
    project = ProjectService.get_by_id(project_id)

    if not project:
        return error_response('Project not found', 404)

    return api_response(data=[m.to_dict() for m in project.team_members])


@projects_bp.route('/<project_id>/members/<team_member_id>', methods=['POST'])
@require_project_access(allow_owner=True, allow_member=False, allow_manager=True)
def add_project_member(project_id, team_member_id):
    """
    Add a team member to a project (Owner or Manager+ only)

    Response: ApiResponse<Project>
    """
    project = ProjectService.add_team_member(project_id, team_member_id)

    if not project:
        return error_response('Project or team member not found', 404)

    return api_response(
        data=project.to_dict(),
        message='Team member added to project'
    )


@projects_bp.route('/<project_id>/members/<team_member_id>', methods=['DELETE'])
@require_project_access(allow_owner=True, allow_member=False, allow_manager=True)
def remove_project_member(project_id, team_member_id):
    """
    Remove a team member from a project (Owner or Manager+ only)

    Response: ApiResponse<Project>
    """
    project = ProjectService.remove_team_member(project_id, team_member_id)

    if not project:
        return error_response('Project or team member not found', 404)

    return api_response(
        data=project.to_dict(),
        message='Team member removed from project'
    )
