"""
Share Link Model
"""
import uuid
import secrets
from datetime import datetime, timedelta
from app.config.database import db


class ShareLink(db.Model):
    """Model for secure project share links"""
    __tablename__ = 'share_links'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    project = db.relationship('Project', backref='share_links')
    creator = db.relationship('User', backref='created_share_links')

    @staticmethod
    def generate_token():
        """Generate a secure random token (32 bytes = 64 chars URL-safe)"""
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self):
        """Check if link has expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self):
        """Check if link is still valid"""
        return not self.is_expired

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'projectId': self.project_id,
            'token': self.token,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'isExpired': self.is_expired
        }

    def __repr__(self):
        return f'<ShareLink {self.token[:8]}... for project {self.project_id}>'
