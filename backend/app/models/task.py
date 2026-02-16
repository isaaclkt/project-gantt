"""
Task Model
"""
import uuid
from datetime import datetime
from app.config.database import db


class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('todo', 'in-progress', 'review', 'completed'), default='todo', index=True)
    priority = db.Column(db.Enum('low', 'medium', 'high'), default='medium', index=True)
    progress = db.Column(db.Integer, default=0)
    assignee_id = db.Column(db.String(36), db.ForeignKey('team_members.id', ondelete='SET NULL'), index=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """Soft delete the task"""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft deleted task"""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if task is soft deleted"""
        return self.deleted_at is not None

    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'priority': self.priority,
            'progress': self.progress,
            'assigneeId': self.assignee_id,
            'projectId': self.project_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_detailed(self):
        """Convert to dictionary with related data"""
        data = self.to_dict()
        if self.assignee:
            data['assignee'] = self.assignee.to_dict()
        if self.project:
            data['project'] = {
                'id': self.project.id,
                'name': self.project.name,
                'color': self.project.color
            }
        return data

    def __repr__(self):
        return f'<Task {self.name}>'
