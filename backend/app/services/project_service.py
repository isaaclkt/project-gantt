"""
Project Service - Business logic for projects
"""
from datetime import datetime
from typing import Optional, List
from app.config.database import db
from app.models import Project, TeamMember
from app.utils.sanitizer import sanitize_dict, PROJECT_SCHEMA


class ProjectService:
    """Service class for project operations"""

    @staticmethod
    def _sanitize_project_data(data: dict) -> dict:
        """Sanitize project input data before processing."""
        return sanitize_dict(data, PROJECT_SCHEMA)

    @staticmethod
    def get_all(
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> tuple[List[Project], int]:
        """
        Get all projects with optional filtering and pagination
        Returns: (projects, total_count)
        """
        query = Project.query

        if status:
            query = query.filter(Project.status == status)

        # Order by updated_at descending
        query = query.order_by(Project.updated_at.desc())

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        projects = query.offset((page - 1) * limit).limit(limit).all()

        return projects, total

    @staticmethod
    def get_by_id(project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return Project.query.get(project_id)

    @staticmethod
    def create(data: dict) -> Project:
        """
        Create a new project with sanitized input
        """
        # Sanitize input data
        sanitized = ProjectService._sanitize_project_data(data)

        # Parse dates
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

        project = Project(
            name=sanitized.get('name', data['name']),
            description=sanitized.get('description', ''),
            color=sanitized.get('color', '#3B82F6'),
            status=sanitized.get('status', 'planning'),
            start_date=start_date,
            end_date=end_date,
            owner_id=data.get('ownerId')
        )

        # Add team members if provided (IDs only, sanitized by SQLAlchemy)
        team_member_ids = data.get('teamMemberIds', [])
        if team_member_ids and isinstance(team_member_ids, list):
            # Only use valid string IDs
            valid_ids = [tid for tid in team_member_ids if isinstance(tid, str)]
            team_members = TeamMember.query.filter(
                TeamMember.id.in_(valid_ids)
            ).all()
            project.team_members = team_members

        db.session.add(project)
        db.session.commit()

        return project

    @staticmethod
    def update(project_id: str, data: dict) -> Optional[Project]:
        """
        Update an existing project with sanitized input
        """
        project = Project.query.get(project_id)
        if not project:
            return None

        # Sanitize input data
        sanitized = ProjectService._sanitize_project_data(data)

        # Update fields if provided (use sanitized values)
        if 'name' in sanitized:
            project.name = sanitized['name']
        if 'description' in sanitized:
            project.description = sanitized['description']
        if 'color' in sanitized:
            project.color = sanitized['color']
        if 'status' in sanitized:
            project.status = sanitized['status']
        if 'progress' in sanitized:
            project.progress = sanitized['progress']
        if 'startDate' in data:
            project.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        if 'endDate' in data:
            project.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

        # Update team members if provided
        if 'teamMemberIds' in data:
            team_member_ids = data['teamMemberIds']
            if isinstance(team_member_ids, list):
                valid_ids = [tid for tid in team_member_ids if isinstance(tid, str)]
                team_members = TeamMember.query.filter(
                    TeamMember.id.in_(valid_ids)
                ).all()
                project.team_members = team_members

        db.session.commit()

        return project

    @staticmethod
    def delete(project_id: str) -> bool:
        """
        Delete a project
        """
        project = Project.query.get(project_id)
        if not project:
            return False

        db.session.delete(project)
        db.session.commit()

        return True

    @staticmethod
    def get_project_tasks(project_id: str) -> List:
        """Get all tasks for a project"""
        project = Project.query.get(project_id)
        if not project:
            return []
        return project.tasks.all()

    @staticmethod
    def update_progress(project_id: str) -> Optional[Project]:
        """Recalculate and update project progress based on tasks"""
        project = Project.query.get(project_id)
        if not project:
            return None

        project.update_progress()
        db.session.commit()

        return project

    @staticmethod
    def add_team_member(project_id: str, team_member_id: str) -> Optional[Project]:
        """Add a team member to project"""
        project = Project.query.get(project_id)
        team_member = TeamMember.query.get(team_member_id)

        if not project or not team_member:
            return None

        if team_member not in project.team_members:
            project.team_members.append(team_member)
            db.session.commit()

        return project

    @staticmethod
    def remove_team_member(project_id: str, team_member_id: str) -> Optional[Project]:
        """Remove a team member from project"""
        project = Project.query.get(project_id)
        team_member = TeamMember.query.get(team_member_id)

        if not project or not team_member:
            return None

        if team_member in project.team_members:
            project.team_members.remove(team_member)
            db.session.commit()

        return project
