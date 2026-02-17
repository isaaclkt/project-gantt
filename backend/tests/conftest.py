"""
Pytest fixtures for backend tests
"""
import os
import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

# Set testing environment before importing app
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from app.config.database import db as _db
from app.models.user import User, UserSettings
from app.models.project import Project
from app.models.task import Task
from app.models.team_member import TeamMember


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-fixed',
        'SECRET_KEY': 'test-secret-key-fixed',
        'RATELIMIT_ENABLED': False,
    })

    # Disable rate limiter
    from app.utils.rate_limiter import limiter
    limiter.enabled = False

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(autouse=True)
def db_session(app):
    """Provide a clean database for each test"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    user = User(
        id='admin-1',
        name='Admin User',
        email='admin@test.com',
        role='admin',
        department='TI'
    )
    user.set_password('admin12345')
    db_session.session.add(user)
    db_session.session.add(UserSettings(user_id='admin-1'))
    db_session.session.commit()
    return user


@pytest.fixture
def manager_user(db_session):
    """Create a manager user"""
    user = User(
        id='manager-1',
        name='Manager User',
        email='manager@test.com',
        role='manager',
        department='Management'
    )
    user.set_password('manager12345')
    db_session.session.add(user)
    db_session.session.add(UserSettings(user_id='manager-1'))
    db_session.session.commit()
    return user


@pytest.fixture
def member_user(db_session):
    """Create a member user"""
    user = User(
        id='member-1',
        name='Member User',
        email='member@test.com',
        role='member',
        department='Development'
    )
    user.set_password('member12345')
    db_session.session.add(user)
    db_session.session.add(UserSettings(user_id='member-1'))
    db_session.session.commit()
    return user


@pytest.fixture
def viewer_user(db_session):
    """Create a viewer user"""
    user = User(
        id='viewer-1',
        name='Viewer User',
        email='viewer@test.com',
        role='viewer',
        department='External'
    )
    user.set_password('viewer12345')
    db_session.session.add(user)
    db_session.session.add(UserSettings(user_id='viewer-1'))
    db_session.session.commit()
    return user


@pytest.fixture
def team_member(db_session, member_user):
    """Create a team member linked to member_user"""
    tm = TeamMember(
        id='tm-1',
        user_id=member_user.id,
        name=member_user.name,
        email=member_user.email,
        role='Developer',
        department='Development',
        status='active'
    )
    db_session.session.add(tm)
    db_session.session.commit()
    return tm


@pytest.fixture
def sample_project(db_session, manager_user):
    """Create a sample project"""
    today = datetime.now().date()
    project = Project(
        id='proj-1',
        name='Test Project',
        description='A test project',
        color='#3B82F6',
        status='active',
        progress=50,
        start_date=today - timedelta(days=5),
        end_date=today + timedelta(days=15),
        owner_id=manager_user.id
    )
    db_session.session.add(project)
    db_session.session.commit()
    return project


@pytest.fixture
def sample_task(db_session, sample_project, team_member):
    """Create a sample task"""
    today = datetime.now().date()
    task = Task(
        id='task-1',
        name='Test Task',
        description='A test task',
        start_date=today,
        end_date=today + timedelta(days=5),
        status='todo',
        priority='medium',
        progress=0,
        assignee_id=team_member.id,
        project_id=sample_project.id
    )
    db_session.session.add(task)
    db_session.session.commit()
    return task


def _make_token(app, user_id):
    """Create a JWT access token directly (bypass login endpoint)"""
    with app.app_context():
        return create_access_token(identity=user_id)


@pytest.fixture
def admin_headers(app, admin_user):
    """Auth headers for admin user"""
    token = _make_token(app, admin_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def manager_headers(app, manager_user):
    """Auth headers for manager user"""
    token = _make_token(app, manager_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def member_headers(app, member_user):
    """Auth headers for member user"""
    token = _make_token(app, member_user.id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def viewer_headers(app, viewer_user):
    """Auth headers for viewer user"""
    token = _make_token(app, viewer_user.id)
    return {'Authorization': f'Bearer {token}'}
