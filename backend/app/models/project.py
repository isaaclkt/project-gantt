"""
Project Model
"""
import uuid
from datetime import datetime
from app.config.database import db
from app.models.team_member import project_members


class Project(db.Model):
    """Project model"""
    __tablename__ = 'projects'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')
    status = db.Column(db.Enum('planning', 'active', 'on-hold', 'completed'), default='planning', index=True)
    progress = db.Column(db.Integer, default=0)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    team_members = db.relationship(
        'TeamMember',
        secondary=project_members,
        back_populates='projects'
    )

    def calculate_progress(self):
        """Calculate project progress based on tasks"""
        tasks = self.tasks.all()
        if not tasks:
            return 0
        return int(sum(task.progress for task in tasks) / len(tasks))

    def update_progress(self):
        """Update progress based on tasks"""
        self.progress = self.calculate_progress()

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'color': self.color,
            'status': self.status,
            'progress': self.progress,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'teamMemberIds': [member.id for member in self.team_members],
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_with_tasks(self):
        """Convert to dictionary including tasks"""
        data = self.to_dict()
        data['tasks'] = [task.to_dict() for task in self.tasks.all()]
        return data

    def __repr__(self):
        return f'<Project {self.name}>'
