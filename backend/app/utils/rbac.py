"""
Role-Based Access Control (RBAC) System

Provides role definitions, permissions, and decorators for route protection.
"""
from functools import wraps
from enum import Enum
from typing import List, Optional, Callable
from flask import request, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.utils.response import error_response


# ============================================
# Role Definitions
# ============================================

class Role(str, Enum):
    """
    System roles with hierarchical permissions.

    Hierarchy: ADMIN > DEPARTMENT_ADMIN > MANAGER > MEMBER > VIEWER
    """
    ADMIN = 'admin'                     # Full system access
    DEPARTMENT_ADMIN = 'department_admin'  # Manages their department only
    MANAGER = 'manager'                 # Can manage projects and teams
    MEMBER = 'member'                   # Can work on assigned tasks
    VIEWER = 'viewer'                   # Read-only access

    @classmethod
    def values(cls) -> List[str]:
        return [role.value for role in cls]

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls.values()


# Role hierarchy (higher index = more permissions)
ROLE_HIERARCHY = {
    Role.VIEWER.value: 0,
    Role.MEMBER.value: 1,
    Role.MANAGER.value: 2,
    Role.DEPARTMENT_ADMIN.value: 3,
    Role.ADMIN.value: 4,
}


# ============================================
# Permission Definitions
# ============================================

class Permission(str, Enum):
    """Fine-grained permissions for specific actions."""

    # User permissions
    VIEW_USERS = 'view_users'
    MANAGE_USERS = 'manage_users'

    # Project permissions
    VIEW_PROJECTS = 'view_projects'
    CREATE_PROJECTS = 'create_projects'
    EDIT_PROJECTS = 'edit_projects'
    DELETE_PROJECTS = 'delete_projects'
    MANAGE_PROJECT_MEMBERS = 'manage_project_members'
    EXPORT_PROJECTS = 'export_projects'

    # Task permissions
    VIEW_TASKS = 'view_tasks'
    CREATE_TASKS = 'create_tasks'
    EDIT_TASKS = 'edit_tasks'
    DELETE_TASKS = 'delete_tasks'
    ASSIGN_TASKS = 'assign_tasks'

    # Team permissions
    VIEW_TEAM = 'view_team'
    MANAGE_TEAM = 'manage_team'

    # Department Admin permissions
    MANAGE_DEPARTMENT_MEMBERS = 'manage_department_members'
    MANAGE_DEPARTMENT_PROJECTS = 'manage_department_projects'

    # Admin permissions
    MANAGE_DEPARTMENTS = 'manage_departments'
    MANAGE_ROLES = 'manage_roles'
    SYSTEM_SETTINGS = 'system_settings'


# Role-to-Permission mapping
ROLE_PERMISSIONS = {
    Role.VIEWER.value: [
        Permission.VIEW_USERS,
        Permission.VIEW_PROJECTS,
        Permission.VIEW_TASKS,
        Permission.VIEW_TEAM,
    ],
    Role.MEMBER.value: [
        Permission.VIEW_USERS,
        Permission.VIEW_PROJECTS,
        Permission.VIEW_TASKS,
        Permission.VIEW_TEAM,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,  # Only own tasks (checked separately)
    ],
    Role.MANAGER.value: [
        Permission.VIEW_USERS,
        Permission.VIEW_PROJECTS,
        Permission.CREATE_PROJECTS,
        Permission.EDIT_PROJECTS,
        Permission.MANAGE_PROJECT_MEMBERS,
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.DELETE_TASKS,
        Permission.ASSIGN_TASKS,
        Permission.VIEW_TEAM,
        Permission.MANAGE_TEAM,
        Permission.EXPORT_PROJECTS,
    ],
    Role.DEPARTMENT_ADMIN.value: [
        # Department admin can manage their department
        Permission.VIEW_USERS,
        Permission.VIEW_PROJECTS,
        Permission.CREATE_PROJECTS,
        Permission.EDIT_PROJECTS,
        Permission.MANAGE_PROJECT_MEMBERS,
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.DELETE_TASKS,
        Permission.ASSIGN_TASKS,
        Permission.VIEW_TEAM,
        Permission.MANAGE_TEAM,
        Permission.MANAGE_DEPARTMENT_MEMBERS,
        Permission.MANAGE_DEPARTMENT_PROJECTS,
        Permission.EXPORT_PROJECTS,
    ],
    Role.ADMIN.value: [
        # Admin has all permissions
        Permission.VIEW_USERS,
        Permission.MANAGE_USERS,
        Permission.VIEW_PROJECTS,
        Permission.CREATE_PROJECTS,
        Permission.EDIT_PROJECTS,
        Permission.DELETE_PROJECTS,
        Permission.MANAGE_PROJECT_MEMBERS,
        Permission.VIEW_TASKS,
        Permission.CREATE_TASKS,
        Permission.EDIT_TASKS,
        Permission.DELETE_TASKS,
        Permission.ASSIGN_TASKS,
        Permission.VIEW_TEAM,
        Permission.MANAGE_TEAM,
        Permission.MANAGE_DEPARTMENTS,
        Permission.MANAGE_ROLES,
        Permission.SYSTEM_SETTINGS,
        Permission.EXPORT_PROJECTS,
    ],
}


# ============================================
# Permission Checking Functions
# ============================================

def get_user_role(user_id: str) -> Optional[str]:
    """Get user's role from database."""
    from app.services import UserService
    user = UserService.get_by_id(user_id)
    if user:
        return user.role or Role.MEMBER.value
    return None


def get_current_user():
    """Get the current authenticated user object."""
    from app.services import UserService
    user_id = get_jwt_identity()
    if user_id:
        return UserService.get_by_id(user_id)
    return None


def has_role(user_role: str, required_role: str) -> bool:
    """
    Check if user has at least the required role level.

    Args:
        user_role: The user's current role
        required_role: The minimum required role

    Returns:
        True if user's role level >= required role level
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 999)
    return user_level >= required_level


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        user_role: The user's role
        permission: The required permission

    Returns:
        True if role has the permission
    """
    role_perms = ROLE_PERMISSIONS.get(user_role, [])
    return permission in role_perms


def is_project_owner(user_id: str, project_id: str) -> bool:
    """Check if user is the owner of a project."""
    from app.services import ProjectService
    project = ProjectService.get_by_id(project_id)
    if project:
        return project.owner_id == user_id
    return False


def is_project_member(user_id: str, project_id: str) -> bool:
    """Check if user is a member of a project."""
    from app.services import ProjectService
    from app.models import TeamMember

    project = ProjectService.get_by_id(project_id)
    if not project:
        return False

    # Check if user's team member is in the project
    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member:
        return team_member in project.team_members
    return False


def is_task_assignee(user_id: str, task_id: str) -> bool:
    """Check if user is assigned to a task."""
    from app.services import TaskService
    from app.models import TeamMember

    task = TaskService.get_by_id(task_id)
    if not task:
        return False

    team_member = TeamMember.query.filter_by(user_id=user_id).first()
    if team_member:
        return task.assignee_id == team_member.id
    return False


# ============================================
# Authorization Decorators
# ============================================

def require_auth(f):
    """
    Decorator to require authentication and load user into g.current_user.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        from app.services import UserService
        user = UserService.get_by_id(user_id)

        if not user:
            return error_response('User not found', 404)

        if not user.is_active:
            return error_response('User account is deactivated', 403)

        # Store user in flask g object for access in route
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def require_role(required_role: str):
    """
    Decorator to require a minimum role level.

    Usage:
        @require_role(Role.MANAGER.value)
        def admin_only_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            from app.services import UserService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            user_role = user.role or Role.MEMBER.value

            if not has_role(user_role, required_role):
                return error_response(
                    f'Insufficient permissions. Required role: {required_role}',
                    403
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.

    Usage:
        @require_permission(Permission.DELETE_PROJECTS)
        def delete_project_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            from app.services import UserService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            user_role = user.role or Role.MEMBER.value

            if not has_permission(user_role, permission):
                return error_response(
                    f'Permission denied: {permission.value}',
                    403
                )

            g.current_user = user
            return f(*args, **kwargs)

        return decorated_function
    return decorator


def require_admin(f):
    """Shortcut decorator for admin-only routes."""
    return require_role(Role.ADMIN.value)(f)


def require_manager(f):
    """Shortcut decorator for manager-and-above routes."""
    return require_role(Role.MANAGER.value)(f)


def require_project_access(allow_owner: bool = True, allow_member: bool = True, allow_manager: bool = True):
    """
    Decorator to check project-level access.

    Args:
        allow_owner: Allow project owner
        allow_member: Allow project team members
        allow_manager: Allow managers (regardless of membership)

    Usage:
        @require_project_access(allow_owner=True, allow_member=False)
        def owner_only_route(project_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            project_id = kwargs.get('project_id')

            if not project_id:
                return error_response('Project ID required', 400)

            from app.services import UserService, ProjectService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            project = ProjectService.get_by_id(project_id)
            if not project:
                return error_response('Project not found', 404)

            user_role = user.role or Role.MEMBER.value

            # Admin always has access
            if has_role(user_role, Role.ADMIN.value):
                g.current_user = user
                return f(*args, **kwargs)

            # Check manager access
            if allow_manager and has_role(user_role, Role.MANAGER.value):
                g.current_user = user
                return f(*args, **kwargs)

            # Check owner access
            if allow_owner and is_project_owner(user_id, project_id):
                g.current_user = user
                return f(*args, **kwargs)

            # Check member access
            if allow_member and is_project_member(user_id, project_id):
                g.current_user = user
                return f(*args, **kwargs)

            return error_response('Access denied to this project', 403)

        return decorated_function
    return decorator


def require_task_access(allow_assignee: bool = True, allow_project_member: bool = True):
    """
    Decorator to check task-level READ access (participant-level).

    Grants access to managers+, the task assignee, or any member of the task's
    project. It does NOT guarantee write permission — a read-only role such as
    'viewer' can pass this check. For mutating endpoints use
    require_task_write_access instead.

    Args:
        allow_assignee: Allow task assignee
        allow_project_member: Allow any project team member
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            task_id = kwargs.get('task_id')

            if not task_id:
                return error_response('Task ID required', 400)

            from app.services import UserService, TaskService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            task = TaskService.get_by_id(task_id)
            if not task:
                return error_response('Task not found', 404)

            user_role = user.role or Role.MEMBER.value

            # Admin/Manager always has access
            if has_role(user_role, Role.MANAGER.value):
                g.current_user = user
                return f(*args, **kwargs)

            # Check assignee access
            if allow_assignee and is_task_assignee(user_id, task_id):
                g.current_user = user
                return f(*args, **kwargs)

            # Check project member access
            if allow_project_member and is_project_member(user_id, task.project_id):
                g.current_user = user
                return f(*args, **kwargs)

            return error_response('Access denied to this task', 403)

        return decorated_function
    return decorator


def require_task_write_access(f):
    """
    Decorator for task WRITE operations (update, status, progress).

    A user may modify a task only when BOTH conditions hold:

      1. Their role grants write capability (Permission.EDIT_TASKS). This
         explicitly excludes read-only roles such as 'viewer', even when the
         viewer is the assignee or a member of the project.
      2. They have access to this specific task: manager and above, the task's
         assignee, or a member of the task's project.

    This separates *reading* a task (participant-level, see
    require_task_access) from *modifying* it (permission-gated).
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        task_id = kwargs.get('task_id')

        if not task_id:
            return error_response('Task ID required', 400)

        from app.services import UserService, TaskService
        user = UserService.get_by_id(user_id)

        if not user:
            return error_response('User not found', 404)

        if not user.is_active:
            return error_response('User account is deactivated', 403)

        task = TaskService.get_by_id(task_id)
        if not task:
            return error_response('Task not found', 404)

        user_role = user.role or Role.MEMBER.value

        # Gate 1: read-only roles (e.g. viewer) can never modify a task.
        if not has_permission(user_role, Permission.EDIT_TASKS):
            return error_response('Read-only role cannot modify tasks', 403)

        # Gate 2: scope the write to tasks this user can actually reach.
        # Manager+ can modify any task.
        if has_role(user_role, Role.MANAGER.value):
            g.current_user = user
            return f(*args, **kwargs)

        # Members: only their own assigned tasks or tasks in their projects.
        if is_task_assignee(user_id, task_id):
            g.current_user = user
            return f(*args, **kwargs)

        if is_project_member(user_id, task.project_id):
            g.current_user = user
            return f(*args, **kwargs)

        return error_response('Access denied to this task', 403)

    return decorated_function


def require_self_or_admin(user_id_param: str = 'user_id'):
    """
    Decorator to allow access only to self or admin.

    Usage:
        @require_self_or_admin('user_id')
        def update_profile(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            target_user_id = kwargs.get(user_id_param)

            from app.services import UserService
            user = UserService.get_by_id(current_user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            user_role = user.role or Role.MEMBER.value

            # Allow if admin or accessing own resource
            if has_role(user_role, Role.ADMIN.value) or current_user_id == target_user_id:
                g.current_user = user
                return f(*args, **kwargs)

            return error_response('Access denied', 403)

        return decorated_function
    return decorator


# ============================================
# Department Admin Functions
# ============================================

def get_user_department_id(user_id: str) -> Optional[str]:
    """Get the department ID for a user."""
    from app.services import UserService
    user = UserService.get_by_id(user_id)
    if user:
        return user.department_id
    return None


def is_department_admin_of(user_id: str, department_id: str) -> bool:
    """
    Check if user is the admin of a specific department.

    Args:
        user_id: The user's ID
        department_id: The department ID to check

    Returns:
        True if user is the admin of that department
    """
    from app.models import Department
    department = Department.query.get(department_id)
    if department:
        return department.admin_id == user_id
    return False


def is_user_in_department(user_id: str, department_id: str) -> bool:
    """Check if a user belongs to a specific department."""
    from app.services import UserService
    user = UserService.get_by_id(user_id)
    if user:
        return user.department_id == department_id
    return False


def require_department_admin(f):
    """Shortcut decorator for department admin routes."""
    return require_role(Role.DEPARTMENT_ADMIN.value)(f)


def require_department_access(allow_own_department: bool = True):
    """
    Decorator to check department-level access.

    For department admins, this checks if the target resource
    belongs to their department.

    Args:
        allow_own_department: Allow access if target is in user's department
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()

            from app.services import UserService
            user = UserService.get_by_id(user_id)

            if not user:
                return error_response('User not found', 404)

            if not user.is_active:
                return error_response('User account is deactivated', 403)

            user_role = user.role or Role.MEMBER.value

            # Admin always has access
            if has_role(user_role, Role.ADMIN.value):
                g.current_user = user
                return f(*args, **kwargs)

            # For department admin, check department membership
            if user_role == Role.DEPARTMENT_ADMIN.value and allow_own_department:
                # Get target member's department from kwargs
                target_member_id = kwargs.get('member_id')

                if target_member_id:
                    from app.models import TeamMember
                    target_member = TeamMember.query.get(target_member_id)

                    if target_member and target_member.user:
                        # Check if target is in same department
                        if target_member.user.department_id == user.department_id:
                            g.current_user = user
                            return f(*args, **kwargs)
                        else:
                            return error_response('Você só pode gerenciar membros do seu departamento', 403)

                # If no specific member, allow access (for listing)
                g.current_user = user
                return f(*args, **kwargs)

            # For regular managers, use standard permission check
            if has_role(user_role, Role.MANAGER.value):
                g.current_user = user
                return f(*args, **kwargs)

            return error_response('Permissão negada', 403)

        return decorated_function
    return decorator


# ============================================
# Department Scoping Functions
# ============================================

def check_project_department_scope(user_id: str, project_id: str) -> bool:
    """
    Check if user has access to a project based on department scope.

    Department admins can only access projects owned by users in their department.

    Args:
        user_id: The user's ID
        project_id: The project ID to check

    Returns:
        True if user has access, False otherwise
    """
    from app.services import UserService, ProjectService
    user = UserService.get_by_id(user_id)
    project = ProjectService.get_by_id(project_id)

    if not user or not project:
        return False

    # Admin: unrestricted.
    if user.role == Role.ADMIN.value:
        return True

    # Department admin: restricted to their own department. A project's
    # department is its explicit department_id (with an owner-derived fallback
    # for legacy rows that predate the column).
    if user.role == Role.DEPARTMENT_ADMIN.value:
        project_dept_id = project.department_id
        if project_dept_id is None and project.owner:
            project_dept_id = project.owner.department_id
        return (
            project_dept_id is not None
            and project_dept_id == user.department_id
        )

    # Everyone else (manager, member, viewer) has read access. These decorators
    # guard read-only routes only; write operations are gated separately by
    # require_project_access / require_task_write_access / require_permission.
    # This keeps single-resource reads consistent with the global listing,
    # which already returns all projects/tasks to these roles.
    return True


def check_task_department_scope(user_id: str, task_id: str) -> bool:
    """
    Check if user has access to a task based on department scope.

    Args:
        user_id: The user's ID
        task_id: The task ID to check

    Returns:
        True if user has access, False otherwise
    """
    from app.services import TaskService
    task = TaskService.get_by_id(task_id)

    if not task:
        return False

    # Check project scope instead (tasks belong to projects)
    return check_project_department_scope(user_id, task.project_id)


# ============================================
# Department Scoping for Listings / Queries
# ============================================

def requires_department_scope(user) -> bool:
    """
    Whether this user's data visibility must be limited to their own department.

    Only 'department_admin' is department-scoped: they administer a single
    department and must never see projects/tasks from other departments.
    'admin' is global; 'manager', 'member' and 'viewer' keep the system's
    existing (non department-scoped) listing behavior.
    """
    if user is None:
        return False
    role = user.role or Role.MEMBER.value
    return role == Role.DEPARTMENT_ADMIN.value


def _project_department_filter(dept_id, Project, User):
    """
    SQL predicate: a project belongs to `dept_id`.

    Source of truth is the explicit Project.department_id. For legacy rows that
    still have a NULL department_id, fall back to the owner's department so no
    project silently escapes the scope during the data transition.
    """
    from sqlalchemy import or_, and_
    return or_(
        Project.department_id == dept_id,
        and_(Project.department_id.is_(None), User.department_id == dept_id)
    )


def scope_project_query(query, user):
    """
    Restrict a Project query to the user's department when required.

    A project's department is its explicit department_id (with an owner-derived
    fallback for legacy rows). A department_admin without a department sees
    nothing (fail closed), so scope can never silently widen into a global
    listing.
    """
    if not requires_department_scope(user):
        return query

    from sqlalchemy import false
    from app.models import User, Project

    dept_id = user.department_id
    if not dept_id:
        return query.filter(false())

    # Outer join so projects whose department_id is set but whose owner is NULL
    # still match on the explicit column.
    return (
        query.outerjoin(User, Project.owner_id == User.id)
             .filter(_project_department_filter(dept_id, Project, User))
    )


def scope_task_query(query, user):
    """
    Restrict a Task query to the user's department when required.

    A task inherits its department from its project. Mirrors scope_project_query
    (explicit Project.department_id with owner fallback) and fails closed for a
    department_admin with no department.
    """
    if not requires_department_scope(user):
        return query

    from sqlalchemy import false
    from app.models import User, Project, Task

    dept_id = user.department_id
    if not dept_id:
        return query.filter(false())

    return (
        query.join(Project, Task.project_id == Project.id)
             .outerjoin(User, Project.owner_id == User.id)
             .filter(_project_department_filter(dept_id, Project, User))
    )


def require_project_department_scope(f):
    """
    Decorator to require department scope for project access.

    Ensures department admins can only access projects in their department.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        project_id = kwargs.get('project_id')

        if not project_id:
            return error_response('Project ID required', 400)

        from app.services import UserService, ProjectService
        user = UserService.get_by_id(user_id)

        if not user:
            return error_response('User not found', 404)

        if not user.is_active:
            return error_response('User account is deactivated', 403)

        # A non-existent project is a 404, not an authorization failure. Only a
        # project that exists but is outside the user's department is a 403.
        if not ProjectService.get_by_id(project_id):
            return error_response('Project not found', 404)

        if not check_project_department_scope(user_id, project_id):
            return error_response('Access denied to this project', 403)

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def require_task_department_scope(f):
    """
    Decorator to require department scope for task access.

    Ensures department admins can only access tasks in projects from their department.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        task_id = kwargs.get('task_id')

        if not task_id:
            return error_response('Task ID required', 400)

        from app.services import UserService, TaskService
        user = UserService.get_by_id(user_id)

        if not user:
            return error_response('User not found', 404)

        if not user.is_active:
            return error_response('User account is deactivated', 403)

        # A non-existent task is a 404, not an authorization failure. Only a task
        # that exists but is outside the user's department is a 403.
        if not TaskService.get_by_id(task_id):
            return error_response('Task not found', 404)

        if not check_task_department_scope(user_id, task_id):
            return error_response('Access denied to this task', 403)

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function