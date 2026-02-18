"""
Audit Service - Business logic for audit logging
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from flask import request
from app.config.database import db
from app.models import AuditLog
from flask_jwt_extended import get_jwt_identity


class AuditService:
    """Service class for audit log operations"""

    # Audit action constants
    AUTH = 'AUTH'
    USER = 'USER'
    PROJECT = 'PROJECT'
    TASK = 'TASK'
    TEAM = 'TEAM'
    DEPARTMENT = 'DEPARTMENT'
    INVITE = 'INVITE'
    SHARE = 'SHARE'

    # Specific actions
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    CREATED = 'CREATED'
    UPDATED = 'UPDATED'
    DELETED = 'DELETED'
    REVOKED = 'REVOKED'
    ACCEPTED = 'ACCEPTED'

    @staticmethod
    def log(
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """
        Log an audit entry

        Args:
            action: The action being performed (e.g., 'LOGIN', 'PROJECT_CREATED')
            resource_type: Type of resource (e.g., 'user', 'project', 'task')
            resource_id: ID of the resource
            details: Additional details (JSON)
            user_id: User ID (uses current user if not provided)
            ip_address: IP address (extracts from request if not provided)
            user_agent: User agent (extracts from request if not provided)

        Returns:
            AuditLog: The created log entry
        """
        if user_id is None:
            try:
                user_id = get_jwt_identity()
            except:
                user_id = None

        if ip_address is None:
            ip_address = AuditService._get_client_ip()

        if user_agent is None:
            user_agent = request.headers.get('User-Agent', '')[:500] if request else ''

        return AuditLog.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_login(user_id: str):
        """Log a user login"""
        return AuditService.log(
            action=f'{AuditService.AUTH}.{AuditService.LOGIN}',
            resource_type='auth',
            resource_id=user_id,
            details={'action': 'user_login'}
        )

    @staticmethod
    def log_logout(user_id: str):
        """Log a user logout"""
        return AuditService.log(
            action=f'{AuditService.AUTH}.{AuditService.LOGOUT}',
            resource_type='auth',
            resource_id=user_id,
            details={'action': 'user_logout'}
        )

    @staticmethod
    def log_resource_created(resource_type: str, resource_id: str, details: Dict = None):
        """Log creation of a resource"""
        return AuditService.log(
            action=f'{resource_type}.{AuditService.CREATED}',
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )

    @staticmethod
    def log_resource_updated(resource_type: str, resource_id: str, details: Dict = None):
        """Log update of a resource"""
        return AuditService.log(
            action=f'{resource_type}.{AuditService.UPDATED}',
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )

    @staticmethod
    def log_resource_deleted(resource_type: str, resource_id: str, details: Dict = None):
        """Log deletion of a resource"""
        return AuditService.log(
            action=f'{resource_type}.{AuditService.DELETED}',
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )

    @staticmethod
    def log_invite_created(invite_id: str, email: str, role: str, department_id: str = None):
        """Log creation of an invite"""
        return AuditService.log(
            action=f'{AuditService.INVITE}.{AuditService.CREATED}',
            resource_type='invite',
            resource_id=invite_id,
            details={
                'email': email,
                'role': role,
                'department_id': department_id
            }
        )

    @staticmethod
    def log_invite_accepted(invite_id: str, user_id: str, email: str):
        """Log acceptance of an invite"""
        return AuditService.log(
            action=f'{AuditService.INVITE}.{AuditService.ACCEPTED}',
            resource_type='invite',
            resource_id=invite_id,
            details={
                'email': email,
                'new_user_id': user_id
            }
        )

    @staticmethod
    def log_invite_revoked(invite_id: str, email: str):
        """Log revocation of an invite"""
        return AuditService.log(
            action=f'{AuditService.INVITE}.{AuditService.REVOKED}',
            resource_type='invite',
            resource_id=invite_id,
            details={'email': email}
        )

    @staticmethod
    def log_share_link_created(share_link_id: str, project_id: str, expires_in_days: int):
        """Log creation of a share link"""
        return AuditService.log(
            action=f'{AuditService.SHARE}.{AuditService.CREATED}',
            resource_type='share_link',
            resource_id=share_link_id,
            details={
                'project_id': project_id,
                'expires_in_days': expires_in_days
            }
        )

    @staticmethod
    def log_share_link_revoked(share_link_id: str, project_id: str):
        """Log revocation of a share link"""
        return AuditService.log(
            action=f'{AuditService.SHARE}.{AuditService.REVOKED}',
            resource_type='share_link',
            resource_id=share_link_id,
            details={'project_id': project_id}
        )

    @staticmethod
    def get_by_resource(resource_type: str, resource_id: str = None, limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs for a specific resource

        Args:
            resource_type: Type of resource
            resource_id: ID of the resource (optional, returns all for type if None)
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog entries
        """
        query = AuditLog.query.filter_by(resource_type=resource_type)
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_by_user(user_id: str, limit: int = 100) -> List[AuditLog]:
        """
        Get audit logs for a specific user

        Args:
            user_id: ID of the user
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog entries
        """
        return AuditLog.query.filter_by(user_id=user_id)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def get_recent(days: int = 30, limit: int = 100) -> List[AuditLog]:
        """
        Get recent audit logs

        Args:
            days: Number of days to look back
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog entries
        """
        since = datetime.utcnow() - timedelta(days=days)
        return AuditLog.query.filter(AuditLog.created_at >= since)\
            .order_by(AuditLog.created_at.desc())\
            .limit(limit)\
            .all()

    @staticmethod
    def _get_client_ip() -> str:
        """Extract client IP from request"""
        if not request:
            return None

        # Check for forwarded headers (proxy/CDN)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        return request.remote_addr

    @staticmethod
    def cleanup_old_logs(days: int = 90) -> int:
        """
        Delete audit logs older than specified days

        Args:
            days: Number of days to keep logs

        Returns:
            Number of deleted logs
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = AuditLog.query.filter(AuditLog.created_at < cutoff).delete()
        db.session.commit()
        return deleted
