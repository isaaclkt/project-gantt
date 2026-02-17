"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
from app.config import get_config, init_db
from app.routes import register_routes


def create_app(config_name=None):
    """
    Application factory for creating Flask app instances

    Args:
        config_name: Configuration name ('development', 'testing', 'production')

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Ensure upload directories exist
    _init_upload_dirs(app)

    # Initialize extensions
    _init_extensions(app)

    # Register blueprints
    register_routes(app)

    # Register error handlers
    _register_error_handlers(app)

    # Register CLI commands
    _register_cli_commands(app)

    return app


def _init_upload_dirs(app):
    """Create upload directories if they don't exist"""
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    avatars_dir = os.path.join(upload_folder, 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)


def _init_extensions(app):
    """Initialize Flask extensions"""
    # CORS - Use origins from environment configuration
    cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:3000'])
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Database
    init_db(app)

    # Initialize Token Blacklist (Redis-backed in production)
    from app.utils.token_blacklist import token_blacklist
    token_blacklist.init_app(app)

    # Initialize JWT
    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)

    # Register token blacklist checker
    from app.routes.auth import check_if_token_revoked
    jwt.token_in_blocklist_loader(check_if_token_revoked)

    # Store jwt instance in app for access in routes
    app.jwt = jwt

    # Initialize Rate Limiter
    _init_rate_limiter(app)


def _init_rate_limiter(app):
    """Initialize rate limiting"""
    from app.utils.rate_limiter import limiter
    limiter.init_app(app)


def _register_error_handlers(app):
    """Register error handlers"""
    from app.utils import error_response
    from app.utils.rate_limiter import rate_limit_exceeded_handler

    # Rate limit error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return rate_limit_exceeded_handler(e)

    @app.errorhandler(400)
    def bad_request(error):
        return error_response('Bad request', 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return error_response('Unauthorized', 401)

    @app.errorhandler(403)
    def forbidden(error):
        return error_response('Forbidden', 403)

    @app.errorhandler(404)
    def not_found(error):
        return error_response('Resource not found', 404)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response('Method not allowed', 405)

    @app.errorhandler(500)
    def internal_error(error):
        return error_response('Internal server error', 500)


def _register_cli_commands(app):
    """Register custom CLI commands"""
    import click
    from app.config.database import db

    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        click.echo('Database initialized.')

    @app.cli.command('seed-db')
    def seed_db_command():
        """Seed the database with sample data."""
        from app.models import User, UserSettings, TeamMember, Project, Task
        from datetime import datetime, timedelta

        # Check if data already exists
        if User.query.first():
            click.echo('Database already has data. Skipping seed.')
            return

        # Create users with RBAC roles
        # Format: (id, name, email, password, system_role, department)
        # System roles: admin, manager, member, viewer
        users_data = [
            ('u0', 'Admin Sistema', 'admin@empresa.com', 'admin123', 'admin', 'TI'),
            ('u1', 'Ana Silva', 'ana.silva@empresa.com', 'password123', 'manager', 'Gestão'),
            ('u2', 'Carlos Santos', 'carlos.santos@empresa.com', 'password123', 'member', 'Desenvolvimento'),
            ('u3', 'Marina Costa', 'marina.costa@empresa.com', 'password123', 'member', 'Desenvolvimento'),
            ('u4', 'Pedro Oliveira', 'pedro.oliveira@empresa.com', 'password123', 'member', 'Design'),
            ('u5', 'Julia Ferreira', 'julia.ferreira@empresa.com', 'password123', 'member', 'Qualidade'),
            ('u6', 'Rafael Mendes', 'rafael.mendes@empresa.com', 'password123', 'manager', 'Infraestrutura'),
            ('u7', 'Cliente Exemplo', 'cliente@empresa.com', 'viewer123', 'viewer', 'Externo'),
        ]

        click.echo('Creating users...')
        for uid, name, email, password, role, department in users_data:
            user = User(
                id=uid,
                name=name,
                email=email,
                role=role,
                department=department
            )
            user.set_password(password)
            db.session.add(user)

            settings = UserSettings(user_id=uid)
            db.session.add(settings)

        click.echo(f'  Created {len(users_data)} users (1 admin, 2 managers, 4 members, 1 viewer)')

        # Create team members (job titles, not system roles)
        # Format: (id, user_id, name, email, job_title, department, status)
        team_data = [
            ('tm0', 'u0', 'Admin Sistema', 'admin@empresa.com', 'System Administrator', 'TI', 'active'),
            ('tm1', 'u1', 'Ana Silva', 'ana.silva@empresa.com', 'Project Manager', 'Gestão', 'active'),
            ('tm2', 'u2', 'Carlos Santos', 'carlos.santos@empresa.com', 'Frontend Developer', 'Desenvolvimento', 'active'),
            ('tm3', 'u3', 'Marina Costa', 'marina.costa@empresa.com', 'Backend Developer', 'Desenvolvimento', 'away'),
            ('tm4', 'u4', 'Pedro Oliveira', 'pedro.oliveira@empresa.com', 'UI/UX Designer', 'Design', 'active'),
            ('tm5', 'u5', 'Julia Ferreira', 'julia.ferreira@empresa.com', 'QA Engineer', 'Qualidade', 'offline'),
            ('tm6', 'u6', 'Rafael Mendes', 'rafael.mendes@empresa.com', 'DevOps Engineer', 'Infraestrutura', 'active'),
        ]

        click.echo('Creating team members...')
        for tmid, uid, name, email, job_title, department, status in team_data:
            tm = TeamMember(
                id=tmid,
                user_id=uid,
                name=name,
                email=email,
                role=job_title,
                department=department,
                status=status
            )
            db.session.add(tm)

        db.session.flush()
        click.echo(f'  Created {len(team_data)} team members')

        # Create projects
        click.echo('Creating projects...')
        today = datetime.now().date()
        projects_data = [
            ('p1', 'Website Redesign', 'Redesign completo do website corporativo', '#3B82F6', 'active', 65, -10, 20, 'u1'),
            ('p2', 'Mobile App', 'Desenvolvimento do aplicativo mobile', '#10B981', 'active', 35, -5, 30, 'u1'),
            ('p3', 'API Integration', 'Integração com APIs de terceiros', '#F59E0B', 'planning', 10, 5, 25, 'u3'),
            ('p4', 'Security Audit', 'Auditoria de segurança do sistema', '#EF4444', 'on-hold', 20, -15, 10, 'u6'),
            ('p5', 'Documentation Update', 'Atualização da documentação técnica', '#8B5CF6', 'completed', 100, -30, -5, 'u1'),
        ]

        for pid, name, desc, color, status, progress, start_offset, end_offset, owner_id in projects_data:
            project = Project(
                id=pid,
                name=name,
                description=desc,
                color=color,
                status=status,
                progress=progress,
                start_date=today + timedelta(days=start_offset),
                end_date=today + timedelta(days=end_offset),
                owner_id=owner_id
            )
            db.session.add(project)

        db.session.flush()
        click.echo(f'  Created {len(projects_data)} projects')

        # Add team members to projects
        click.echo('Assigning team members to projects...')
        p1 = Project.query.get('p1')
        p2 = Project.query.get('p2')
        p3 = Project.query.get('p3')
        p4 = Project.query.get('p4')
        p5 = Project.query.get('p5')

        tm1 = TeamMember.query.get('tm1')
        tm2 = TeamMember.query.get('tm2')
        tm3 = TeamMember.query.get('tm3')
        tm4 = TeamMember.query.get('tm4')
        tm5 = TeamMember.query.get('tm5')
        tm6 = TeamMember.query.get('tm6')

        p1.team_members.extend([tm1, tm2, tm4])
        p2.team_members.extend([tm1, tm2, tm3])
        p3.team_members.extend([tm3, tm6])
        p4.team_members.extend([tm5, tm6])
        p5.team_members.extend([tm1, tm5])

        # Create tasks
        click.echo('Creating tasks...')
        tasks_data = [
            ('t1', 'Design da Homepage', 'Criar novo design', -10, -3, 'completed', 'high', 100, 'tm4', 'p1'),
            ('t2', 'Implementação Frontend', 'Desenvolver componentes', -5, 5, 'in-progress', 'high', 60, 'tm2', 'p1'),
            ('t3', 'Revisão de Código', 'Code review do frontend', 3, 7, 'todo', 'medium', 0, 'tm3', 'p1'),
            ('t4', 'Testes de Usabilidade', 'Testes com usuários', 8, 12, 'todo', 'medium', 0, 'tm5', 'p1'),
            ('t5', 'Setup do Projeto Mobile', 'Config ambiente', -5, -2, 'completed', 'high', 100, 'tm2', 'p2'),
            ('t6', 'Desenvolvimento de Telas', 'Criar telas principais', -2, 10, 'in-progress', 'high', 30, 'tm2', 'p2'),
            ('t7', 'API Backend Mobile', 'Desenvolver endpoints', 1, 15, 'review', 'high', 80, 'tm3', 'p2'),
            ('t8', 'Análise de Requisitos', 'Levantar requisitos', 5, 10, 'todo', 'medium', 0, 'tm3', 'p3'),
            ('t9', 'Scan de Vulnerabilidades', 'Executar ferramentas', -15, -10, 'completed', 'high', 100, 'tm6', 'p4'),
            ('t10', 'Relatório de Segurança', 'Documentar vulnerabilidades', -10, 5, 'in-progress', 'high', 40, 'tm6', 'p4'),
        ]

        for tid, name, desc, start_offset, end_offset, status, priority, progress, assignee_id, project_id in tasks_data:
            task = Task(
                id=tid,
                name=name,
                description=desc,
                start_date=today + timedelta(days=start_offset),
                end_date=today + timedelta(days=end_offset),
                status=status,
                priority=priority,
                progress=progress,
                assignee_id=assignee_id,
                project_id=project_id
            )
            db.session.add(task)

        click.echo(f'  Created {len(tasks_data)} tasks')

        db.session.commit()

        click.echo('')
        click.echo('=' * 50)
        click.echo('Database seeded successfully!')
        click.echo('=' * 50)
        click.echo('')
        click.echo('Test accounts created:')
        click.echo('')
        click.echo('  ADMIN:')
        click.echo('    Email: admin@empresa.com')
        click.echo('    Password: admin123')
        click.echo('')
        click.echo('  MANAGER:')
        click.echo('    Email: ana.silva@empresa.com')
        click.echo('    Password: password123')
        click.echo('')
        click.echo('  MEMBER:')
        click.echo('    Email: carlos.santos@empresa.com')
        click.echo('    Password: password123')
        click.echo('')
        click.echo('  VIEWER:')
        click.echo('    Email: cliente@empresa.com')
        click.echo('    Password: viewer123')
        click.echo('')

    @app.cli.command('reset-db')
    def reset_db_command():
        """Reset the database (drop all tables and recreate)."""
        if click.confirm('This will delete all data. Are you sure?'):
            db.drop_all()
            db.create_all()
            click.echo('Database reset complete.')
