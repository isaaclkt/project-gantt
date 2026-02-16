"""
Team Member Model
"""
import uuid
from datetime import datetime
from app.config.database import db


# Association table for project members
project_members = db.Table(
    'project_members',
    db.Column('id', db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    db.Column('project_id', db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
    db.Column('team_member_id', db.String(36), db.ForeignKey('team_members.id', ondelete='CASCADE'), nullable=False),
    db.Column('role', db.String(100), default='member'),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow),
    db.UniqueConstraint('project_id', 'team_member_id', name='unique_project_member')
)


class TeamMember(db.Model):
    """Team member model"""
    __tablename__ = 'team_members'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id', ondelete='SET NULL'), nullable=True)
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)

    # Campos mantidos para compatibilidade (serão preenchidos do user)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    avatar = db.Column(db.String(500))
    role = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))

    status = db.Column(db.Enum('active', 'away', 'offline'), default='active')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    assigned_tasks = db.relationship('Task', backref='assignee', lazy='dynamic')
    projects = db.relationship(
        'Project',
        secondary=project_members,
        back_populates='team_members'
    )
    role_ref = db.relationship('Role', backref='team_members')
    department_ref = db.relationship('Department', backref='team_members')

    def soft_delete(self):
        """Soft delete the team member"""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft deleted team member"""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if team member is soft deleted"""
        return self.deleted_at is not None

    def sync_from_user(self):
        """Sync data from related user"""
        if self.user:
            self.name = self.user.name
            self.email = self.user.email
            self.avatar = self.user.avatar

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'userId': self.user_id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar or f'https://api.dicebear.com/7.x/avataaars/svg?seed={self.name}',
            'role': self.role,
            'jobTitle': self.job_title,
            'department': self.department,
            'status': self.status,
            'joinedAt': self.joined_at.isoformat() if self.joined_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<TeamMember {self.name}>'
