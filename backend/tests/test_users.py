"""
Tests for administrative user creation (POST /api/users)

These complement the public-registration tests in test_auth.py. Together they
prove the role-governance rule:
  - public registration  -> role can never be elevated (forced to member)
  - administrative create -> elevated roles allowed, but only for an authorized
                             (admin) caller and only for valid, known roles
"""
import pytest
from app.models import User


class TestAdminCreateUser:
    """Tests for POST /api/users (requires MANAGE_USERS -> admin only)"""

    def test_admin_can_create_user_with_elevated_role(self, client, admin_headers):
        """Cenário 4: admin autorizado consegue criar usuário com role elevada."""
        response = client.post('/api/users', json={
            'name': 'New Manager',
            'email': 'new-manager@test.com',
            'password': 'password12345',
            'role': 'manager'
        }, headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 201
        assert data['data']['role'] == 'manager'

        # Confirm persistence
        user = User.query.filter_by(email='new-manager@test.com').first()
        assert user is not None
        assert user.role == 'manager'

    def test_admin_create_user_defaults_to_member_without_role(self, client, admin_headers):
        """Sem 'role' no payload, o fluxo administrativo usa a role padrão segura."""
        response = client.post('/api/users', json={
            'name': 'No Role User',
            'email': 'no-role@test.com',
            'password': 'password12345'
        }, headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 201
        assert data['data']['role'] == 'member'

    def test_admin_create_user_rejects_unknown_role(self, client, admin_headers):
        """Role fora do conjunto conhecido é rejeitada (400), não criada."""
        response = client.post('/api/users', json={
            'name': 'Weird Role',
            'email': 'weird-role@test.com',
            'password': 'password12345',
            'role': 'superuser'
        }, headers=admin_headers)

        assert response.status_code == 400
        assert User.query.filter_by(email='weird-role@test.com').first() is None

    def test_member_cannot_create_user(self, client, member_headers):
        """Usuário não-autorizado (member) não pode criar usuários -> 403."""
        response = client.post('/api/users', json={
            'name': 'Should Fail',
            'email': 'should-fail@test.com',
            'password': 'password12345',
            'role': 'admin'
        }, headers=member_headers)

        assert response.status_code == 403
        assert User.query.filter_by(email='should-fail@test.com').first() is None

    def test_unauthenticated_cannot_create_user(self, client, db_session):
        """Sem token, criação administrativa é bloqueada -> 401."""
        response = client.post('/api/users', json={
            'name': 'Anon',
            'email': 'anon@test.com',
            'password': 'password12345',
            'role': 'admin'
        })

        assert response.status_code == 401
