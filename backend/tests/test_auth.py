"""
Tests for authentication endpoints
"""
import pytest


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, admin_user):
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin12345'
        })
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert 'accessToken' in data['data']
        assert 'refreshToken' in data['data']
        assert data['data']['user']['email'] == 'admin@test.com'

    def test_login_wrong_password(self, client, admin_user):
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'noone@test.com',
            'password': 'password123'
        })

        assert response.status_code == 401

    def test_login_missing_fields(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com'
        })

        assert response.status_code == 400

    def test_login_no_json(self, client):
        response = client.post('/api/auth/login', data='not json')

        assert response.status_code in [400, 415]


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_success(self, client, db_session):
        response = client.post('/api/auth/register', json={
            'name': 'New User',
            'email': 'newuser@test.com',
            'password': 'password12345'
        })
        data = response.get_json()

        assert response.status_code == 201
        assert data['success'] is True
        assert 'accessToken' in data['data']
        assert data['data']['user']['name'] == 'New User'

    def test_register_duplicate_email(self, client, admin_user):
        response = client.post('/api/auth/register', json={
            'name': 'Duplicate',
            'email': 'admin@test.com',
            'password': 'password12345'
        })

        assert response.status_code == 409

    def test_register_short_password(self, client, db_session):
        response = client.post('/api/auth/register', json={
            'name': 'Short Pass',
            'email': 'short@test.com',
            'password': '1234567'
        })

        assert response.status_code == 400

    def test_register_missing_fields(self, client, db_session):
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com'
        })

        assert response.status_code == 400


class TestRefreshToken:
    """Tests for POST /api/auth/refresh"""

    def test_refresh_success(self, client, admin_user):
        # Login first
        login_resp = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin12345'
        })
        refresh_token = login_resp.get_json()['data']['refreshToken']

        # Refresh
        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        data = response.get_json()

        assert response.status_code == 200
        assert 'accessToken' in data['data']

    def test_refresh_with_access_token_fails(self, client, admin_user):
        login_resp = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin12345'
        })
        access_token = login_resp.get_json()['data']['accessToken']

        response = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {access_token}'
        })

        assert response.status_code == 422

    def test_refresh_no_token(self, client):
        response = client.post('/api/auth/refresh')

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_success(self, client, admin_headers):
        response = client.post('/api/auth/logout', headers=admin_headers)

        assert response.status_code == 200

    def test_logout_no_token(self, client):
        response = client.post('/api/auth/logout')

        assert response.status_code == 401


class TestVerifyToken:
    """Tests for GET /api/auth/verify"""

    def test_verify_valid_token(self, client, admin_headers):
        response = client.get('/api/auth/verify', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['valid'] is True

    def test_verify_no_token(self, client):
        response = client.get('/api/auth/verify')

        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for GET /api/auth/me"""

    def test_get_me_success(self, client, admin_headers, admin_user):
        response = client.get('/api/auth/me', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['email'] == 'admin@test.com'
        assert data['data']['name'] == 'Admin User'

    def test_get_me_no_token(self, client):
        response = client.get('/api/auth/me')

        assert response.status_code == 401


class TestChangePassword:
    """Tests for POST /api/auth/change-password"""

    def test_change_password_success(self, client, admin_headers):
        response = client.post('/api/auth/change-password', json={
            'currentPassword': 'admin12345',
            'newPassword': 'newpassword123'
        }, headers=admin_headers)

        assert response.status_code == 200

        # Verify new password works
        login_resp = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'newpassword123'
        })
        assert login_resp.status_code == 200

    def test_change_password_wrong_current(self, client, admin_headers):
        response = client.post('/api/auth/change-password', json={
            'currentPassword': 'wrongpassword',
            'newPassword': 'newpassword123'
        }, headers=admin_headers)

        assert response.status_code == 401

    def test_change_password_too_short(self, client, admin_headers):
        response = client.post('/api/auth/change-password', json={
            'currentPassword': 'admin12345',
            'newPassword': '1234567'
        }, headers=admin_headers)

        assert response.status_code == 400
