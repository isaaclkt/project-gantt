"""
Security Tests - Critical functionality validation

Tests for:
1. Department admin scoping - cannot access cross-department resources
2. Share link revocation - revoked/expired links block access
3. Invite acceptance - creates user and marks used_at
"""
import pytest
from app import create_app
from app.config.database import db
from app.models import User, Project, Department, Invite, ShareLink, TeamMember, AuditLog


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def db_setup(app):
    """Setup test data"""
    with app.app_context():
        # Create departments
        dept1 = Department(id='d1', name='TI')
        dept2 = Department(id='d2', name='Marketing')
        db.session.add_all([dept1, dept2])

        # Create users
        admin = User(id='u1', name='Admin', email='admin@test.com', role='admin')
        admin.set_password('admin123')

        dept_admin1 = User(id='u2', name='Dept Admin TI', email='deptadmin1@test.com', role='department_admin', department_id='d1')
        dept_admin1.set_password('dept123')

        dept_admin2 = User(id='u3', name='Dept Admin MKT', email='deptadmin2@test.com', role='department_admin', department_id='d2')
        dept_admin2.set_password('dept123')

        manager1 = User(id='u4', name='Manager TI', email='manager1@test.com', role='manager', department_id='d1')
        manager1.set_password('manager123')

        manager2 = User(id='u5', name='Manager MKT', email='manager2@test.com', role='manager', department_id='d2')
        manager2.set_password('manager123')

        db.session.add_all([admin, dept_admin1, dept_admin2, manager1, manager2])

        # Create team members
        tm1 = TeamMember(id='tm1', user_id='u2', name='Dept Admin TI', email='deptadmin1@test.com', role='Department Admin')
        tm2 = TeamMember(id='tm2', user_id='u4', name='Manager TI', email='manager1@test.com', role='Manager')
        db.session.add_all([tm1, tm2])

        # Create projects
        proj1 = Project(id='p1', name='Project TI', owner_id='u4', start_date='2024-01-01', end_date='2024-12-31')
        proj2 = Project(id='p2', name='Project MKT', owner_id='u5', start_date='2024-01-01', end_date='2024-12-31')
        db.session.add_all([proj1, proj2])

        db.session.commit()

        yield {
            'admin': admin,
            'dept_admin1': dept_admin1,
            'dept_admin2': dept_admin2,
            'manager1': manager1,
            'manager2': manager2,
            'proj1': proj1,
            'proj2': proj2,
            'dept1': dept1,
            'dept2': dept2
        }


def _login(client, email, password):
    """Helper to login and get token"""
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    return response.json['data']['accessToken']


class TestDepartmentAdminScoping:
    """Test that department admins cannot access resources from other departments"""

    def test_department_admin_cannot_get_cross_department_project(self, app, db_setup, client):
        """Department admin should not be able to access project from another department"""
        token = _login(client, 'deptadmin1@test.com', 'dept123')

        # Try to access project from different department
        response = client.get(
            f'/api/projects/{db_setup["proj2"].id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 403
        assert 'Access denied' in response.json['message']

    def test_department_admin_can_get_own_department_project(self, app, db_setup, client):
        """Department admin should be able to access project from their own department"""
        token = _login(client, 'deptadmin1@test.com', 'dept123')

        # Access project from same department
        response = client.get(
            f'/api/projects/{db_setup["proj1"].id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert response.json['data']['id'] == db_setup["proj1"].id

    def test_admin_can_access_any_project(self, app, db_setup, client):
        """Admin should be able to access any project"""
        token = _login(client, 'admin@test.com', 'admin123')

        # Access project from any department
        response = client.get(
            f'/api/projects/{db_setup["proj2"].id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        assert response.json['data']['id'] == db_setup["proj2"].id


class TestShareLinkRevocation:
    """Test that revoked and expired share links block public access"""

    def test_revoked_share_link_blocks_access(self, app, db_setup, client):
        """Revoked share links should block access"""
        from datetime import datetime, timedelta

        # Create share link
        share_link = ShareLink(
            id='sl1',
            project_id='p1',
            token='test_token_123',
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_by='u1'
        )
        db.session.add(share_link)
        db.session.commit()

        # Revoke the link
        share_link.revoke()
        db.session.commit()

        # Try to access with revoked token
        response = client.get(f'/api/share/public/{share_link.token}')

        assert response.status_code == 404
        assert 'inválido ou expirado' in response.json['message']

    def test_expired_share_link_blocks_access(self, app, db_setup, client):
        """Expired share links should block access"""
        from datetime import datetime, timedelta

        # Create expired share link
        share_link = ShareLink(
            id='sl2',
            project_id='p1',
            token='expired_token_123',
            expires_at=datetime.utcnow() - timedelta(days=1),
            created_by='u1'
        )
        db.session.add(share_link)
        db.session.commit()

        # Try to access with expired token
        response = client.get(f'/api/share/public/{share_link.token}')

        assert response.status_code == 404
        assert 'inválido ou expirado' in response.json['message']

    def test_valid_share_link_allows_access(self, app, db_setup, client):
        """Valid share links should allow access and update tracking"""
        from datetime import datetime, timedelta

        # Create valid share link
        share_link = ShareLink(
            id='sl3',
            project_id='p1',
            token='valid_token_123',
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_by='u1',
            access_count=0
        )
        db.session.add(share_link)
        db.session.commit()

        # Access with valid token
        response = client.get(f'/api/share/public/{share_link.token}')

        assert response.status_code == 200

        # Verify tracking was updated
        db.session.refresh(share_link)
        assert share_link.access_count == 1
        assert share_link.last_access_at is not None


class TestInviteAcceptance:
    """Test invite acceptance creates user and marks used_at"""

    def test_valid_invite_creates_user_and_marks_used(self, app, db_setup, client):
        """Accepting a valid invite should create a user and mark invite as used"""
        from datetime import datetime, timedelta

        # Create invite
        invite = Invite(
            id='inv1',
            token='invite_token_123',
            email='newuser@test.com',
            role='member',
            department_id='d1',
            created_by='u1',
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(invite)
        db.session.commit()

        # Accept invite
        response = client.post('/api/invites/invite_token_123/accept', json={
            'password': 'newpassword123'
        })

        assert response.status_code == 201

        # Verify user was created
        user = User.query.filter_by(email='newuser@test.com').first()
        assert user is not None
        assert user.role == 'member'
        assert user.department_id == 'd1'

        # Verify invite is marked as used
        db.session.refresh(invite)
        assert invite.used_at is not None

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(resource_id='inv1').first()
        assert audit_log is not None
        assert 'ACCEPTED' in audit_log.action

    def test_expired_invite_blocks_acceptance(self, app, db_setup, client):
        """Expired invites should block acceptance"""
        from datetime import datetime, timedelta

        # Create expired invite
        invite = Invite(
            id='inv2',
            token='expired_invite_token',
            email='expired@test.com',
            role='member',
            created_by='u1',
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        db.session.add(invite)
        db.session.commit()

        # Try to accept expired invite
        response = client.post('/api/invites/expired_invite_token/accept', json={
            'password': 'password123'
        })

        assert response.status_code == 400
        assert 'inválido' in response.json['message'] or 'expirado' in response.json['message']

        # Verify user was NOT created
        user = User.query.filter_by(email='expired@test.com').first()
        assert user is None


class TestAuditLogging:
    """Test that audit logs are created for critical actions"""

    def test_invite_created_logs_audit(self, app, db_setup, client):
        """Creating an invite should create an audit log"""
        token = _login(client, 'admin@test.com', 'admin123')

        # Create invite
        response = client.post(
            '/api/invites',
            json={
                'email': 'audit_test@test.com',
                'role': 'member'
            },
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(action='INVITE.CREATED').first()
        assert audit_log is not None
        assert audit_log.resource_type == 'invite'
        assert audit_log.user_id == 'u1'  # admin

    def test_invite_revoked_logs_audit(self, app, db_setup, client):
        """Revoking an invite should create an audit log"""
        from datetime import datetime, timedelta

        # Create invite
        invite = Invite(
            id='inv3',
            token='to_revoke_token',
            email='torevoke@test.com',
            role='member',
            created_by='u1',
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(invite)
        db.session.commit()

        token = _login(client, 'admin@test.com', 'admin123')

        # Revoke invite
        response = client.delete(
            f'/api/invites/{invite.id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(action='INVITE.REVOKED').first()
        assert audit_log is not None
        assert audit_log.resource_id == 'inv3'

    def test_share_link_created_logs_audit(self, app, db_setup, client):
        """Creating a share link should create an audit log"""
        token = _login(client, 'manager1@test.com', 'manager123')

        # Create share link
        response = client.post(
            f'/api/share/projects/{db_setup["proj1"].id}',
            json={'expiresInDays': 7},
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(action='SHARE.CREATED').first()
        assert audit_log is not None
        assert audit_log.resource_type == 'share_link'

    def test_share_link_revoked_logs_audit(self, app, db_setup, client):
        """Revoking a share link should create an audit log"""
        from datetime import datetime, timedelta

        # Create share link
        share_link = ShareLink(
            id='sl4',
            project_id='p1',
            token='to_revoke_share',
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_by='u4'
        )
        db.session.add(share_link)
        db.session.commit()

        token = _login(client, 'manager1@test.com', 'manager123')

        # Revoke share link
        response = client.delete(
            f'/api/share/links/{share_link.id}',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200

        # Verify audit log was created
        audit_log = AuditLog.query.filter_by(action='SHARE.REVOKED').first()
        assert audit_log is not None
        assert audit_log.resource_id == 'sl4'
