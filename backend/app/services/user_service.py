"""
User Service - Business logic for users and settings
"""
from typing import Optional, List
from app.config.database import db
from app.models import User, UserSettings
from app.utils.sanitizer import sanitize_dict, sanitize_email, USER_SCHEMA


class UserService:
    """Service class for user operations"""

    # All roles a user may legitimately hold in the system.
    ASSIGNABLE_ROLES = {'admin', 'department_admin', 'manager', 'member', 'viewer'}

    # Safe default role for self-service (public) registration.
    # Public sign-ups must NEVER be able to grant themselves an elevated role,
    # so the system always assigns the lowest working role. 'member' is chosen
    # to match the User model default and lets the account do useful work
    # (edit assigned tasks) without any privileged capability.
    DEFAULT_PUBLIC_ROLE = 'member'

    @staticmethod
    def _sanitize_user_data(data: dict) -> dict:
        """Sanitize user input data before processing."""
        sanitized = sanitize_dict(data, USER_SCHEMA)

        # Additional sanitization for avatar URL
        if 'avatar' in data and data['avatar']:
            avatar = data['avatar']
            # Only allow valid URL patterns (http/https or local upload paths)
            if isinstance(avatar, str) and (avatar.startswith(('http://', 'https://')) or avatar.startswith('/')):
                sanitized['avatar'] = avatar[:500]  # Limit URL length

        return sanitized

    @staticmethod
    def get_all(page: int = 1, limit: int = 50) -> tuple[List[User], int]:
        """
        Get all users with pagination
        Returns: (users, total_count)
        """
        query = User.query.filter(User.is_active == True)
        query = query.order_by(User.name.asc())

        total = query.count()
        users = query.offset((page - 1) * limit).limit(limit).all()

        return users, total

    @staticmethod
    def get_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def _create_user(data: dict, role: str) -> User:
        """
        Internal user creation.

        SECURITY: the role is ALWAYS taken from the explicit `role` argument
        decided by the caller — never from the request payload. This keeps the
        service layer safe even if a route forgets to strip a client-supplied
        role (defense in depth).
        """
        # Sanitize input data (role in the payload is deliberately ignored here)
        sanitized = UserService._sanitize_user_data(data)
        name = sanitized.get('name', data['name'])

        user = User(
            name=name,
            email=sanitize_email(data['email']),
            avatar=sanitized.get('avatar') or f"https://api.dicebear.com/7.x/avataaars/svg?seed={name}",
            role=role,
            department=sanitized.get('department'),
            phone=data.get('phone'),
            timezone=data.get('timezone', 'America/Sao_Paulo')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.flush()

        # Create default settings for user
        settings = UserSettings(user_id=user.id)
        db.session.add(settings)

        db.session.commit()

        return user

    @staticmethod
    def register(data: dict) -> User:
        """
        Public self-service registration.

        SECURITY: the role is always forced to DEFAULT_PUBLIC_ROLE. Any `role`
        present in the payload is ignored, so a user can never sign up as
        admin / department_admin / manager through the public endpoint.
        """
        return UserService._create_user(data, role=UserService.DEFAULT_PUBLIC_ROLE)

    @staticmethod
    def create_by_admin(data: dict) -> User:
        """
        Administrative user creation.

        Must be called only from an authorized route (MANAGE_USERS). The role
        may be elevated, but must be one of the known, valid system roles —
        arbitrary/unknown roles are rejected with a ValueError.
        """
        requested_role = data.get('role') or UserService.DEFAULT_PUBLIC_ROLE
        if requested_role not in UserService.ASSIGNABLE_ROLES:
            raise ValueError(f'Invalid role: {requested_role}')
        return UserService._create_user(data, role=requested_role)

    @staticmethod
    def update(user_id: str, data: dict) -> Optional[User]:
        """
        Update an existing user with sanitized input
        """
        user = User.query.get(user_id)
        if not user:
            return None

        # Sanitize input data
        sanitized = UserService._sanitize_user_data(data)

        if 'name' in sanitized:
            user.name = sanitized['name']
        if 'email' in sanitized:
            user.email = sanitized['email']
        if 'avatar' in sanitized:
            user.avatar = sanitized['avatar']
        # Only update role when a valid role was provided. The enum sanitizer
        # returns None for unknown roles, so we must never wipe the existing role.
        if sanitized.get('role'):
            user.role = sanitized['role']
        if 'department' in sanitized:
            user.department = sanitized['department']
        if 'phone' in data:
            user.phone = data['phone']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'status' in data:
            user.status = data['status']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()

        return user

    @staticmethod
    def delete(user_id: str) -> bool:
        """
        Soft delete a user (set is_active to False)
        """
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = False
        db.session.commit()

        return True

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        Returns user if valid, None otherwise
        """
        user = User.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def get_profile(user_id: str) -> Optional[dict]:
        """Get user profile in frontend format"""
        user = User.query.get(user_id)
        if not user:
            return None
        return user.to_profile_dict()

    @staticmethod
    def update_profile(user_id: str, data: dict) -> Optional[User]:
        """Update user profile"""
        return UserService.update(user_id, data)


class UserSettingsService:
    """Service class for user settings operations"""

    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[UserSettings]:
        """Get settings by user ID"""
        return UserSettings.query.filter_by(user_id=user_id).first()

    @staticmethod
    def create_default(user_id: str) -> UserSettings:
        """Create default settings for a user"""
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()
        return settings

    @staticmethod
    def update(user_id: str, data: dict) -> Optional[UserSettings]:
        """
        Update user settings
        """
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserSettingsService.create_default(user_id)

        if 'theme' in data:
            settings.theme = data['theme']
        if 'language' in data:
            settings.language = data['language']
        if 'notifications' in data:
            settings.notifications = data['notifications']
        if 'displayPreferences' in data:
            settings.display_preferences = data['displayPreferences']

        db.session.commit()

        return settings
