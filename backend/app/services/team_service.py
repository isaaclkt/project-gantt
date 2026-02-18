"""
Team Service - Business logic for team members
"""
import uuid
from typing import Optional, List
from app.config.database import db
from app.models import TeamMember, User, UserSettings


class TeamService:
    """Service class for team member operations"""

    @staticmethod
    def get_all(
        department: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[TeamMember], int]:
        """
        Get all team members with optional filtering and pagination
        Returns: (team_members, total_count)
        """
        query = TeamMember.query

        if department:
            query = query.filter(TeamMember.department == department)
        if status:
            query = query.filter(TeamMember.status == status)

        # Order by name
        query = query.order_by(TeamMember.name.asc())

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        team_members = query.offset((page - 1) * limit).limit(limit).all()

        return team_members, total

    @staticmethod
    def get_by_id(team_member_id: str) -> Optional[TeamMember]:
        """Get team member by ID"""
        return TeamMember.query.get(team_member_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[TeamMember]:
        """Get team member by email"""
        return TeamMember.query.filter_by(email=email).first()

    @staticmethod
    def create(data: dict) -> TeamMember:
        """
        Create a new team member (and associated user if not provided)

        Args:
            data: dict with keys:
                - name: str (required)
                - email: str (required)
                - role: str (required) - job role/title
                - password: str (required when creating new user, min 8 chars)
                - department: str (optional)
                - status: str (optional, default 'active')
                - userId: str (optional, link to existing user)
        """
        user_id = data.get('userId')
        password = data.get('password')

        # If no user_id provided, create a new user first
        if not user_id:
            # Check if user with this email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                user_id = existing_user.id
            else:
                # Validate password for new user
                if not password:
                    raise ValueError('Senha é obrigatória para criar um novo membro')
                if len(password) < 8:
                    raise ValueError('Senha deve ter no mínimo 8 caracteres')

                # Create new user with provided password
                user = User(
                    id=str(uuid.uuid4()),
                    name=data['name'],
                    email=data['email'],
                    avatar=data.get('avatar') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={data['name']}",
                    role='member',  # Default system role
                    department=data.get('department'),
                    status=data.get('status', 'active')
                )
                user.set_password(password)  # Use admin-provided password
                db.session.add(user)
                db.session.flush()  # Get the user ID
                user_id = user.id

                # Create user settings
                settings = UserSettings(user_id=user_id)
                db.session.add(settings)

        team_member = TeamMember(
            name=data['name'],
            email=data['email'],
            avatar=data.get('avatar') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={data['name']}",
            role=data['role'],
            department=data.get('department'),
            job_title=data.get('jobTitle'),
            status=data.get('status', 'active'),
            user_id=user_id
        )

        db.session.add(team_member)
        db.session.commit()

        return team_member

    @staticmethod
    def update(team_member_id: str, data: dict) -> Optional[TeamMember]:
        """
        Update an existing team member
        """
        team_member = TeamMember.query.get(team_member_id)
        if not team_member:
            return None

        # Update fields if provided
        if 'name' in data:
            team_member.name = data['name']
        if 'email' in data:
            team_member.email = data['email']
        if 'avatar' in data:
            team_member.avatar = data['avatar']
        if 'role' in data:
            team_member.role = data['role']
        if 'department' in data:
            team_member.department = data['department']
        if 'status' in data:
            team_member.status = data['status']

        db.session.commit()

        return team_member

    @staticmethod
    def delete(team_member_id: str) -> bool:
        """
        Delete a team member
        """
        team_member = TeamMember.query.get(team_member_id)
        if not team_member:
            return False

        db.session.delete(team_member)
        db.session.commit()

        return True

    @staticmethod
    def update_status(team_member_id: str, status: str) -> Optional[TeamMember]:
        """Quick update just the status of a team member"""
        team_member = TeamMember.query.get(team_member_id)
        if not team_member:
            return None

        team_member.status = status
        db.session.commit()

        return team_member

    @staticmethod
    def get_departments() -> List[str]:
        """Get list of all unique departments"""
        results = db.session.query(TeamMember.department).distinct().filter(
            TeamMember.department.isnot(None)
        ).all()
        return [r[0] for r in results if r[0]]

    @staticmethod
    def get_by_project(project_id: str) -> List[TeamMember]:
        """Get all team members assigned to a project"""
        from app.models import Project
        project = Project.query.get(project_id)
        if not project:
            return []
        return project.team_members
