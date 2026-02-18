"""
Department and Role Models
"""
import uuid
from datetime import datetime
from app.config.database import db


class Department(db.Model):
    """Department model"""
    __tablename__ = 'departments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    admin_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship - use string reference to avoid circular import
    admin = db.relationship('User', foreign_keys=[admin_id], backref='administered_department', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'adminId': self.admin_id,
            'adminName': self.admin.name if self.admin else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Department {self.name}>'


class Role(db.Model):
    """Role model"""
    __tablename__ = 'roles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Role {self.name}>'
