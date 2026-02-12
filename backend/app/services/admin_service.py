"""
Admin Service - Business logic for departments and roles
"""
import uuid
from typing import Optional, List
from app.config.database import db
from app.models import Department, Role


class DepartmentService:
    """Service class for department operations"""

    @staticmethod
    def get_all() -> List[Department]:
        """Get all departments"""
        return Department.query.order_by(Department.name.asc()).all()

    @staticmethod
    def get_by_id(department_id: str) -> Optional[Department]:
        """Get department by ID"""
        return Department.query.get(department_id)

    @staticmethod
    def get_by_name(name: str) -> Optional[Department]:
        """Get department by name"""
        return Department.query.filter_by(name=name).first()

    @staticmethod
    def create(data: dict) -> Department:
        """Create a new department"""
        department = Department(
            id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(department)
        db.session.commit()
        return department

    @staticmethod
    def update(department_id: str, data: dict) -> Optional[Department]:
        """Update an existing department"""
        department = Department.query.get(department_id)
        if not department:
            return None

        if 'name' in data:
            department.name = data['name']
        if 'description' in data:
            department.description = data['description']

        db.session.commit()
        return department

    @staticmethod
    def delete(department_id: str) -> bool:
        """Delete a department"""
        department = Department.query.get(department_id)
        if not department:
            return False

        db.session.delete(department)
        db.session.commit()
        return True


class RoleService:
    """Service class for role operations"""

    @staticmethod
    def get_all() -> List[Role]:
        """Get all roles"""
        return Role.query.order_by(Role.name.asc()).all()

    @staticmethod
    def get_by_id(role_id: str) -> Optional[Role]:
        """Get role by ID"""
        return Role.query.get(role_id)

    @staticmethod
    def get_by_name(name: str) -> Optional[Role]:
        """Get role by name"""
        return Role.query.filter_by(name=name).first()

    @staticmethod
    def create(data: dict) -> Role:
        """Create a new role"""
        role = Role(
            id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(role)
        db.session.commit()
        return role

    @staticmethod
    def update(role_id: str, data: dict) -> Optional[Role]:
        """Update an existing role"""
        role = Role.query.get(role_id)
        if not role:
            return None

        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']

        db.session.commit()
        return role

    @staticmethod
    def delete(role_id: str) -> bool:
        """Delete a role"""
        role = Role.query.get(role_id)
        if not role:
            return False

        db.session.delete(role)
        db.session.commit()
        return True
