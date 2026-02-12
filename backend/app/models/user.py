"""
User Model
"""
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.config.database import db


class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(500))
    role = db.Column(db.String(100), default='member')
    department = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    timezone = db.Column(db.String(100), default='America/Sao_Paulo')
    status = db.Column(db.Enum('active', 'away', 'offline'), default='active')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    settings = db.relationship('UserSettings', backref='user', uselist=False, cascade='all, delete-orphan')
    team_member = db.relationship('TeamMember', backref='user', uselist=False)
    owned_projects = db.relationship('Project', backref='owner', lazy='dynamic')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar or f'https://api.dicebear.com/7.x/avataaars/svg?seed={self.name}',
            'role': self.role,
            'department': self.department,
            'phone': self.phone,
            'timezone': self.timezone,
            'status': self.status,
            'joinedAt': self.created_at.isoformat() if self.created_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_profile_dict(self):
        """Convert to UserProfile format for frontend"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar or f'https://api.dicebear.com/7.x/avataaars/svg?seed={self.name}',
            'role': self.role,
            'department': self.department or '',
            'phone': self.phone,
            'timezone': self.timezone,
            'joinedAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.name}>'


class UserSettings(db.Model):
    """User settings model"""
    __tablename__ = 'user_settings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    theme = db.Column(db.Enum('light', 'dark', 'system'), default='system')
    language = db.Column(db.String(10), default='pt-BR')
    notifications = db.Column(db.JSON, default=lambda: {
        'email': True,
        'push': True,
        'taskReminders': True,
        'projectUpdates': True
    })
    display_preferences = db.Column(db.JSON, default=lambda: {
        'compactMode': False,
        'showAvatars': True,
        'defaultView': 'gantt'
    })
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notifications': self.notifications or {
                'email': True,
                'push': True,
                'taskReminders': True,
                'projectUpdates': True
            },
            'displayPreferences': self.display_preferences or {
                'compactMode': False,
                'showAvatars': True,
                'defaultView': 'gantt'
            }
        }

    def __repr__(self):
        return f'<UserSettings for user {self.user_id}>'
