"""
Invite Model
For team member invitations
"""
import uuid
import secrets
from datetime import datetime, timedelta
from app.config.database import db


class Invite(db.Model):
    """Model for team member invitations"""
    __tablename__ = 'invites'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    role = db.Column(db.String(100), nullable=False)  # manager, member, viewer
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    password = db.Column(db.String(255))  # Pre-set password (hashed)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used_at = db.Column(db.DateTime, nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    department = db.relationship('Department', backref='invites')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_invites')

    @staticmethod
    def generate_token():
        """Generate a secure random token for invites"""
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self):
        """Check if invite has expired"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self):
        """Check if invite has been used"""
        return self.used_at is not None

    @property
    def is_revoked(self):
        """Check if invite has been revoked"""
        return self.revoked_at is not None

    @property
    def is_valid(self):
        """Check if invite is still valid (not expired, used, or revoked)"""
        return not self.is_expired and not self.is_used and not self.is_revoked

    def use(self):
        """Mark invite as used"""
        self.used_at = datetime.utcnow()

    def revoke(self):
        """Revoke (soft delete) this invite"""
        self.revoked_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'departmentId': self.department_id,
            'departmentName': self.department.name if self.department else None,
            'createdBy': self.created_by,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'usedAt': self.used_at.isoformat() if self.used_at else None,
            'revokedAt': self.revoked_at.isoformat() if self.revoked_at else None,
            'isExpired': self.is_expired,
            'isUsed': self.is_used,
            'isRevoked': self.is_revoked,
            'isValid': self.is_valid,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Invite {self.email}>'