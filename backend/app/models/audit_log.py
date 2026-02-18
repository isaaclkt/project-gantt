"""
Audit Log Model
Tracks all critical actions for security and compliance
"""
import uuid
from datetime import datetime
from app.config.database import db


class AuditLog(db.Model):
    """Model for tracking user actions and system events"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False, index=True)
    resource_id = db.Column(db.String(36), nullable=True)
    details = db.Column(db.JSON, default=dict)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='audit_logs')

    @staticmethod
    def log_action(user_id, action, resource_type, resource_id=None, details=None, ip_address=None, user_agent=None):
        """
        Create a new audit log entry

        Args:
            user_id: ID of the user performing the action (None for system actions)
            action: The action being performed (e.g., 'INVITE_CREATED', 'PROJECT_DELETED')
            resource_type: Type of resource being acted upon (e.g., 'project', 'user', 'invite')
            resource_id: ID of the resource (optional)
            details: Additional details about the action (JSON)
            ip_address: IP address of the requester
            user_agent: User agent string

        Returns:
            AuditLog: The created log entry
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(audit_log)
        db.session.commit()
        return audit_log

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'userName': self.user.name if self.user else 'System',
            'action': self.action,
            'resourceType': self.resource_type,
            'resourceId': self.resource_id,
            'details': self.details or {},
            'ipAddress': self.ip_address,
            'userAgent': self.user_agent,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource_type}:{self.resource_id}>'
