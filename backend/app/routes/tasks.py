"""
Tasks API Routes

Routes are protected with RBAC (Role-Based Access Control).
"""
from flask import Blueprint, request, g
from app.services import TaskService
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
    require_task_access,
    require_task_department_scope,
    Permission
)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


@tasks_bp.route('', methods=['GET'])
@require_auth
@validate_pagination
def get_tasks():
    """
    Get all tasks (requires authentication)

    Query params:
        - projectId: Filter by project
        - status: Filter by status (todo, in-progress, review, completed)
        - assigneeId: Filter by assignee
        - priority: Filter by priority (low, medium, high)
        - page: Page number (default: 1)
        - limit: Items per page (default: 50, max: 100)

    Response: PaginatedResponse<Task[]>
    """
    project_id = request.args.get('projectId')
    status = request.args.get('status')
    assignee_id = request.args.get('assigneeId')
    priority = request.args.get('priority')
    page = request.pagination['page']
    limit = request.pagination['limit']

    tasks, total = TaskService.get_all(
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        page=page,
        limit=limit
    )

    return paginated_response(
        data=[t.to_dict() for t in tasks],
        page=page,
        limit=limit,
        total=total
    )


@tasks_bp.route('/<task_id>', methods=['GET'])
@require_auth
@require_task_department_scope
def get_task(task_id):
    """
    Get a single task by ID (requires authentication)
    Department admins can only access tasks from projects in their department.

    Response: ApiResponse<Task>
    """
    task = TaskService.get_by_id(task_id)

    if not task:
        return error_response('Task not found', 404)

    return api_response(data=task.to_dict_detailed())


@tasks_bp.route('', methods=['POST'])
@require_permission(Permission.CREATE_TASKS)
@validate_json
@validate_required_fields(['name', 'startDate', 'endDate', 'projectId'])
@validate_string_length('name', min_length=1, max_length=255)
@validate_date_range('startDate', 'endDate')
@validate_enum_field('status', ['todo', 'in-progress', 'review', 'completed'])
@validate_enum_field('priority', ['low', 'medium', 'high'])
def create_task():
    """
    Create a new task (requires CREATE_TASKS permission - Member+)

    Body (CreateTaskInput):
        - name: string (required)
        - description: string
        - startDate: string (YYYY-MM-DD, required)
        - endDate: string (YYYY-MM-DD, required)
        - status: 'todo' | 'in-progress' | 'review' | 'completed'
        - priority: 'low' | 'medium' | 'high'
        - assigneeId: string
        - projectId: string (required)

    Response: ApiResponse<Task>
    """
    data = request.get_json()

    try:
        task = TaskService.create(data)
        return api_response(
            data=task.to_dict(),
            message='Task created successfully',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to create task: {str(e)}', 500)


@tasks_bp.route('/<task_id>', methods=['PUT', 'PATCH'])
@require_task_access(allow_assignee=True, allow_project_member=True)
@validate_json
@validate_string_length('name', min_length=1, max_length=255)
@validate_date_range('startDate', 'endDate')
@validate_progress('progress')
@validate_enum_field('status', ['todo', 'in-progress', 'review', 'completed'])
@validate_enum_field('priority', ['low', 'medium', 'high'])
def update_task(task_id):
    """
    Update an existing task (Assignee or Project Member)

    Body (UpdateTaskInput):
        - name: string
        - description: string
        - startDate: string (YYYY-MM-DD)
        - endDate: string (YYYY-MM-DD)
        - status: 'todo' | 'in-progress' | 'review' | 'completed'
        - priority: 'low' | 'medium' | 'high'
        - progress: number (0-100)
        - assigneeId: string | null
        - projectId: string

    Response: ApiResponse<Task>
    """
    data = request.get_json()

    try:
        task = TaskService.update(task_id, data)

        if not task:
            return error_response('Task not found', 404)

        return api_response(
            data=task.to_dict(),
            message='Task updated successfully'
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to update task: {str(e)}', 500)


@tasks_bp.route('/<task_id>', methods=['DELETE'])
@require_permission(Permission.DELETE_TASKS)
def delete_task(task_id):
    """
    Delete a task (requires DELETE_TASKS permission - Manager+)

    Response: ApiResponse<null>
    """
    success = TaskService.delete(task_id)

    if not success:
        return error_response('Task not found', 404)

    return api_response(
        data=None,
        message='Task deleted successfully'
    )


@tasks_bp.route('/<task_id>/status', methods=['PATCH'])
@require_task_access(allow_assignee=True, allow_project_member=True)
@validate_json
@validate_required_fields(['status'])
def update_task_status(task_id):
    """
    Quick update task status (Assignee or Project Member)

    Body:
        - status: 'todo' | 'in-progress' | 'review' | 'completed' (required)

    Response: ApiResponse<Task>
    """
    data = request.get_json()
    status = data['status']

    valid_statuses = ['todo', 'in-progress', 'review', 'completed']
    if status not in valid_statuses:
        return error_response(f'Invalid status. Allowed: {", ".join(valid_statuses)}', 400)

    task = TaskService.update_status(task_id, status)

    if not task:
        return error_response('Task not found', 404)

    return api_response(
        data=task.to_dict(),
        message='Task status updated'
    )


@tasks_bp.route('/<task_id>/progress', methods=['PATCH'])
@require_task_access(allow_assignee=True, allow_project_member=True)
@validate_json
@validate_required_fields(['progress'])
def update_task_progress(task_id):
    """
    Quick update task progress (Assignee or Project Member)

    Body:
        - progress: number (0-100, required)

    Response: ApiResponse<Task>
    """
    data = request.get_json()
    progress = data['progress']

    if not isinstance(progress, (int, float)) or progress < 0 or progress > 100:
        return error_response('Progress must be a number between 0 and 100', 400)

    task = TaskService.update_progress(task_id, int(progress))

    if not task:
        return error_response('Task not found', 404)

    return api_response(
        data=task.to_dict(),
        message='Task progress updated'
    )
