"""
Invite Service - Business logic for team member invitations
"""
from datetime import datetime, timedelta
from typing import Optional, List
from werkzeug.security import generate_password_hash
from app.config.database import db
from app.models import Invite, User, TeamMember, UserSettings, Department
from app.utils.rbac import Role, has_role


class InviteService:
    """Service class for invite operations"""

    # Valid roles for invites (department_admin cannot be invited)
    VALID_INVITE_ROLES = [Role.MANAGER.value, Role.MEMBER.value, Role.VIEWER.value]
    DEFAULT_EXPIRY_DAYS = 7

    @staticmethod
    def create(
        email: str,
        role: str,
        created_by: str,
        department_id: str = None,
        password: str = None,
        expires_in_days: int = None
    ) -> Invite:
        """
        Create a new team member invite

        Args:
            email: Email address of the invitee
            role: Role to assign (manager, member, viewer)
            created_by: ID of the user creating the invite
            department_id: Department to assign (default: creator's department)
            password: Optional pre-set password (will be hashed)
            expires_in_days: Days until expiry (default: 7)

        Returns:
            Invite: The created invite

        Raises:
            ValueError: If role is invalid or department access denied
        """
        # Validate role
        if role not in InviteService.VALID_INVITE_ROLES:
            raise ValueError(f'Invalid role. Allowed: {", ".join(InviteService.VALID_INVITE_ROLES)}')

        # Get creator for department check
        creator = User.query.get(created_by)
        if not creator:
            raise ValueError('Creator not found')

        # Department admin can only invite to their own department
        if creator.role == Role.DEPARTMENT_ADMIN.value:
            if department_id and department_id != creator.department_id:
                raise ValueError('Department admin can only invite to their own department')
            # Default to creator's department
            department_id = creator.department_id
        elif not department_id:
            # Default to creator's department for other roles too
            department_id = creator.department_id

        # Check if department exists
        if department_id:
            dept = Department.query.get(department_id)
            if not dept:
                raise ValueError('Department not found')

        # Hash password if provided
        password_hash = None
        if password:
            password_hash = generate_password_hash(password)

        # Set expiry
        if expires_in_days is None:
            expires_in_days = InviteService.DEFAULT_EXPIRY_DAYS

        invite = Invite(
            token=Invite.generate_token(),
            email=email.lower(),
            role=role,
            department_id=department_id,
            password=password_hash,
            created_by=created_by,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
        )

        db.session.add(invite)
        db.session.commit()

        return invite

    @staticmethod
    def get_by_token(token: str) -> Optional[Invite]:
        """Get invite by token"""
        return Invite.query.filter_by(token=token).first()

    @staticmethod
    def get_valid_by_token(token: str) -> Optional[Invite]:
        """Get invite by token, only if valid"""
        invite = Invite.query.filter_by(token=token).first()
        if invite and invite.is_valid:
            return invite
        return None

    @staticmethod
    def get_by_creator(created_by: str) -> List[Invite]:
        """Get all invites created by a user"""
        return Invite.query.filter_by(created_by=created_by)\
            .order_by(Invite.created_at.desc())\
            .all()

    @staticmethod
    def get_by_department(department_id: str) -> List[Invite]:
        """Get all invites for a department"""
        return Invite.query.filter_by(department_id=department_id)\
            .order_by(Invite.created_at.desc())\
            .all()

    @staticmethod
    def get_by_id(invite_id: str) -> Optional[Invite]:
        """Get invite by ID"""
        return Invite.query.get(invite_id)

    @staticmethod
    def revoke(invite_id: str, revoked_by: str = None) -> bool:
        """
        Revoke an invite (soft delete - sets revoked_at)

        Args:
            invite_id: ID of the invite to revoke
            revoked_by: ID of the user revoking (for audit)

        Returns:
            True if revoked, False if not found
        """
        invite = Invite.query.get(invite_id)
        if not invite:
            return False

        invite.revoke()
        db.session.commit()
        return True

    @staticmethod
    def accept(token: str, password: str = None) -> User:
        """
        Accept an invite and create a user

        Args:
            token: The invite token
            password: Password for the new user (uses pre-set password if not provided)

        Returns:
            User: The newly created user

        Raises:
            ValueError: If invite is invalid/expired/used/revoked or email already exists
        """
        invite = InviteService.get_valid_by_token(token)

        if not invite:
            raise ValueError('Convite inválido, expirado ou revogado')

        # Check if user with this email already exists
        existing_user = User.query.filter_by(email=invite.email).first()
        if existing_user:
            raise ValueError('Já existe uma conta com este e-mail')

        # Use pre-set password if provided, otherwise use the one from accept
        if invite.password and not password:
            # The invite has a pre-set password, user doesn't need to provide one
            password_hash = invite.password
        elif password:
            # User provided their own password
            password_hash = generate_password_hash(password)
        else:
            raise ValueError('Senha obrigatória')

        # Create user
        user = User(
            name=invite.email.split('@')[0],  # Default name from email
            email=invite.email,
            password_hash=password_hash,
            role=invite.role,
            department_id=invite.department_id
        )

        db.session.add(user)
        db.session.flush()  # Get user ID

        # Create user settings
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)

        # Create team member profile
        team_member = TeamMember(
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=invite.role,
            department=invite.department.name if invite.department else None
        )
        db.session.add(team_member)

        # Mark invite as used
        invite.use()

        db.session.commit()

        # Refresh to get relationships
        db.session.refresh(user)

        return user

    @staticmethod
    def cleanup_expired():
        """Delete expired invites (optional cleanup job)"""
        Invite.query.filter(Invite.expires_at < datetime.utcnow()).delete()
        db.session.commit()

    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return Invite.generate_token()
