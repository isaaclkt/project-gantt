"""
Share Link Service - Business logic for project share links
"""
from datetime import datetime, timedelta
from typing import Optional, List
from app.config.database import db
from app.models import ShareLink, Project


class ShareLinkService:
    """Service class for share link operations"""

    DEFAULT_EXPIRY_DAYS = 7

    @staticmethod
    def create(project_id: str, created_by: str, expires_in_days: int = None) -> ShareLink:
        """
        Create a new share link for a project

        Args:
            project_id: ID of the project to share
            created_by: ID of the user creating the link
            expires_in_days: Number of days until expiration (default 7)

        Returns:
            ShareLink: The created share link

        Raises:
            ValueError: If project not found
        """
        if expires_in_days is None:
            expires_in_days = ShareLinkService.DEFAULT_EXPIRY_DAYS

        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            raise ValueError('Projeto não encontrado')

        share_link = ShareLink(
            project_id=project_id,
            token=ShareLink.generate_token(),
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            created_by=created_by
        )

        db.session.add(share_link)
        db.session.commit()

        return share_link

    @staticmethod
    def get_by_token(token: str) -> Optional[ShareLink]:
        """Get share link by token"""
        return ShareLink.query.filter_by(token=token).first()

    @staticmethod
    def get_valid_by_token(token: str) -> Optional[ShareLink]:
        """Get share link by token, only if not expired"""
        share_link = ShareLink.query.filter_by(token=token).first()
        if share_link and share_link.is_valid:
            return share_link
        return None

    @staticmethod
    def get_project_by_token(token: str) -> Optional[Project]:
        """Get project data by share token"""
        share_link = ShareLinkService.get_valid_by_token(token)
        if share_link:
            return share_link.project
        return None

    @staticmethod
    def get_by_project(project_id: str) -> List[ShareLink]:
        """Get all share links for a project"""
        return ShareLink.query.filter_by(project_id=project_id).order_by(ShareLink.created_at.desc()).all()

    @staticmethod
    def get_by_id(link_id: str) -> Optional[ShareLink]:
        """Get share link by ID"""
        return ShareLink.query.get(link_id)

    @staticmethod
    def delete(link_id: str) -> bool:
        """Delete a share link"""
        share_link = ShareLink.query.get(link_id)
        if not share_link:
            return False
        db.session.delete(share_link)
        db.session.commit()
        return True

    @staticmethod
    def delete_expired():
        """Clean up expired share links"""
        ShareLink.query.filter(ShareLink.expires_at < datetime.utcnow()).delete()
        db.session.commit()
