"""
Routes module
"""
from .projects import projects_bp
from .tasks import tasks_bp
from .team import team_bp
from .users import users_bp
from .auth import auth_bp
from .admin import admin_bp
from .insights import insights_bp
from .share import share_bp


def register_routes(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(share_bp)


__all__ = [
    'projects_bp',
    'tasks_bp',
    'team_bp',
    'users_bp',
    'auth_bp',
    'admin_bp',
    'insights_bp',
    'share_bp',
    'register_routes'
]
