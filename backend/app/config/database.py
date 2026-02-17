"""
Database Configuration and Connection
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Migrate
migrate = Migrate()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import models to ensure they're registered
        from app.models import user, project, task, team_member

        # Create tables if they don't exist
        db.create_all()


def reset_db(app):
    """Reset database (for development only)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
