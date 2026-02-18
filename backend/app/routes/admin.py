"""
Admin API Routes - Departments and Roles management

All routes require admin role.
"""
from flask import Blueprint, request
from app.services import DepartmentService, RoleService, UserService
from app.utils import (
    api_response,
    error_response,
    validate_json,
    validate_required_fields
)
from app.utils.rbac import require_admin, require_auth, require_permission, Permission

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ============================================
# Departments Routes
# ============================================

@admin_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """
    Get all departments (any authenticated user)
    Response: ApiResponse<Department[]>
    """
    departments = DepartmentService.get_all()
    return api_response(data=[d.to_dict() for d in departments])


@admin_bp.route('/departments/<department_id>', methods=['GET'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
def get_department(department_id):
    """
    Get a single department by ID (Admin only)
    Response: ApiResponse<Department>
    """
    department = DepartmentService.get_by_id(department_id)
    if not department:
        return error_response('Department not found', 404)
    return api_response(data=department.to_dict())


@admin_bp.route('/departments', methods=['POST'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
@validate_json
@validate_required_fields(['name'])
def create_department():
    """
    Create a new department
    Body: { name: string, description?: string }
    Response: ApiResponse<Department>
    """
    data = request.get_json()

    # Check if already exists
    existing = DepartmentService.get_by_name(data['name'])
    if existing:
        return error_response('Department with this name already exists', 409)

    try:
        department = DepartmentService.create(data)
        return api_response(
            data=department.to_dict(),
            message='Department created successfully',
            status_code=201
        )
    except Exception as e:
        return error_response(f'Failed to create department: {str(e)}', 500)


@admin_bp.route('/departments/<department_id>', methods=['PUT'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
@validate_json
def update_department(department_id):
    """
    Update an existing department
    Body: { name?: string, description?: string }
    Response: ApiResponse<Department>
    """
    data = request.get_json()

    # Check if name already exists (if changing name)
    if 'name' in data:
        existing = DepartmentService.get_by_name(data['name'])
        if existing and existing.id != department_id:
            return error_response('Department with this name already exists', 409)

    department = DepartmentService.update(department_id, data)
    if not department:
        return error_response('Department not found', 404)

    return api_response(
        data=department.to_dict(),
        message='Department updated successfully'
    )


@admin_bp.route('/departments/<department_id>', methods=['DELETE'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
def delete_department(department_id):
    """
    Delete a department (Admin only)
    Response: ApiResponse<null>
    """
    success = DepartmentService.delete(department_id)
    if not success:
        return error_response('Department not found', 404)

    return api_response(data=None, message='Department deleted successfully')


@admin_bp.route('/departments/<department_id>/admin', methods=['PUT'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
@validate_json
@validate_required_fields(['userId'])
def assign_department_admin(department_id):
    """
    Assign an admin to a department (Admin only)

    Body: { userId: string }
    Response: ApiResponse<Department>

    Note: This also updates the user's role to 'department_admin'.
    """
    data = request.get_json()
    user_id = data['userId']

    # Check if department exists
    department = DepartmentService.get_by_id(department_id)
    if not department:
        return error_response('Department not found', 404)

    # Check if user exists
    user = UserService.get_by_id(user_id)
    if not user:
        return error_response('User not found', 404)

    # Check if user is already admin of another department
    from app.models import Department
    existing_dept = Department.query.filter_by(admin_id=user_id).first()
    if existing_dept and existing_dept.id != department_id:
        return error_response(f'Este usuário já é administrador do departamento "{existing_dept.name}"', 409)

    try:
        # Update department admin
        updated_dept = DepartmentService.set_admin(department_id, user_id)

        # Update user role to department_admin
        UserService.update(user_id, {'role': 'department_admin'})

        return api_response(
            data=updated_dept.to_dict(),
            message=f'{user.name} foi definido como administrador do departamento'
        )
    except Exception as e:
        return error_response(f'Falha ao atribuir administrador: {str(e)}', 500)


@admin_bp.route('/departments/<department_id>/admin', methods=['DELETE'])
@require_permission(Permission.MANAGE_DEPARTMENTS)
def remove_department_admin(department_id):
    """
    Remove admin from a department (Admin only)
    Response: ApiResponse<Department>

    Note: This also changes the user's role back to 'manager'.
    """
    # Check if department exists
    department = DepartmentService.get_by_id(department_id)
    if not department:
        return error_response('Department not found', 404)

    if not department.admin_id:
        return error_response('Este departamento não possui um administrador', 400)

    try:
        old_admin_id = department.admin_id

        # Remove admin from department
        updated_dept = DepartmentService.set_admin(department_id, None)

        # Change user role back to manager (or keep as is if admin)
        old_admin = UserService.get_by_id(old_admin_id)
        if old_admin and old_admin.role == 'department_admin':
            UserService.update(old_admin_id, {'role': 'manager'})

        return api_response(
            data=updated_dept.to_dict(),
            message='Administrador removido do departamento'
        )
    except Exception as e:
        return error_response(f'Falha ao remover administrador: {str(e)}', 500)


# ============================================
# Roles Routes
# ============================================

@admin_bp.route('/roles', methods=['GET'])
@require_auth
def get_roles():
    """
    Get all roles (any authenticated user)
    Response: ApiResponse<Role[]>
    """
    roles = RoleService.get_all()
    return api_response(data=[r.to_dict() for r in roles])


@admin_bp.route('/roles/<role_id>', methods=['GET'])
@require_permission(Permission.MANAGE_ROLES)
def get_role(role_id):
    """
    Get a single role by ID (Admin only)
    Response: ApiResponse<Role>
    """
    role = RoleService.get_by_id(role_id)
    if not role:
        return error_response('Role not found', 404)
    return api_response(data=role.to_dict())


@admin_bp.route('/roles', methods=['POST'])
@require_permission(Permission.MANAGE_ROLES)
@validate_json
@validate_required_fields(['name'])
def create_role():
    """
    Create a new role
    Body: { name: string, description?: string }
    Response: ApiResponse<Role>
    """
    data = request.get_json()

    # Check if already exists
    existing = RoleService.get_by_name(data['name'])
    if existing:
        return error_response('Role with this name already exists', 409)

    try:
        role = RoleService.create(data)
        return api_response(
            data=role.to_dict(),
            message='Role created successfully',
            status_code=201
        )
    except Exception as e:
        return error_response(f'Failed to create role: {str(e)}', 500)


@admin_bp.route('/roles/<role_id>', methods=['PUT'])
@require_permission(Permission.MANAGE_ROLES)
@validate_json
def update_role(role_id):
    """
    Update an existing role
    Body: { name?: string, description?: string }
    Response: ApiResponse<Role>
    """
    data = request.get_json()

    # Check if name already exists (if changing name)
    if 'name' in data:
        existing = RoleService.get_by_name(data['name'])
        if existing and existing.id != role_id:
            return error_response('Role with this name already exists', 409)

    role = RoleService.update(role_id, data)
    if not role:
        return error_response('Role not found', 404)

    return api_response(
        data=role.to_dict(),
        message='Role updated successfully'
    )


@admin_bp.route('/roles/<role_id>', methods=['DELETE'])
@require_permission(Permission.MANAGE_ROLES)
def delete_role(role_id):
    """
    Delete a role (Admin only)
    Response: ApiResponse<null>
    """
    success = RoleService.delete(role_id)
    if not success:
        return error_response('Role not found', 404)

    return api_response(data=None, message='Role deleted successfully')
