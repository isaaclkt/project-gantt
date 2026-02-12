"""
Team Service - Business logic for team members
"""
from typing import Optional, List
from app.config.database import db
from app.models import TeamMember


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
        Create a new team member
        """
        team_member = TeamMember(
            name=data['name'],
            email=data['email'],
            avatar=data.get('avatar') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={data['name']}",
            role=data['role'],
            department=data.get('department'),
            status=data.get('status', 'active'),
            user_id=data.get('userId')
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
