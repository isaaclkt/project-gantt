"""
Rate limiting tests.

Ensures that exceeding a rate limit returns a standardized HTTP 429 (never a
500 caused by a broken error handler) and that requests below the limit keep
working normally.

The shared limiter is disabled globally by conftest.py, so this module owns its
own app/client fixtures that re-enable it and reset it afterwards, leaving the
rest of the suite unaffected.
"""
import pytest
from app import create_app
from app.config.database import db as _db
from app.utils.rate_limiter import limiter


@pytest.fixture
def app():
    """App with the rate limiter ENABLED (auth endpoints allow 5/min per IP)."""
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-fixed',
        'SECRET_KEY': 'test-secret-key-fixed',
    })

    # Turn the shared limiter on and start from a clean counter for this test.
    limiter.enabled = True
    limiter.reset()

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

    # Restore the disabled state so other test modules are not throttled.
    limiter.reset()
    limiter.enabled = False


@pytest.fixture
def client(app):
    return app.test_client()


def _spam_login(client, times):
    """Fire `times` login attempts and return the list of status codes."""
    statuses = []
    for _ in range(times):
        resp = client.post('/api/auth/login', json={
            'email': 'nobody@test.com',
            'password': 'wrong-password'
        })
        statuses.append(resp.status_code)
    return statuses


class TestLoginRateLimit:
    """POST /api/auth/login is limited to 5 per minute per IP."""

    def test_exceeding_limit_returns_429_not_500(self, client):
        """Cenário 1: ao estourar o limite, resposta é 429 (nunca 500)."""
        statuses = _spam_login(client, 8)

        assert 429 in statuses, f"expected a 429, got {statuses}"
        assert 500 not in statuses, f"got a 500 (broken handler): {statuses}"

    def test_429_payload_follows_api_contract(self, client):
        """Cenário 3: o JSON do 429 segue o contrato padrão da API."""
        # Drive past the limit and capture the throttled response.
        response = None
        for _ in range(8):
            response = client.post('/api/auth/login', json={
                'email': 'nobody@test.com',
                'password': 'wrong-password'
            })
            if response.status_code == 429:
                break

        assert response is not None
        assert response.status_code == 429

        body = response.get_json()
        assert body is not None
        assert body['success'] is False
        assert body['data'] is None
        assert isinstance(body['message'], str) and body['message']

    def test_requests_below_limit_are_not_throttled(self, client):
        """Cenário 4a: dentro do limite, o endpoint responde normalmente."""
        # 4 attempts (< 5/min) must never be rate limited.
        statuses = _spam_login(client, 4)

        assert 429 not in statuses
        assert 500 not in statuses
        assert all(s == 401 for s in statuses), statuses  # invalid creds -> 401

    def test_valid_login_within_limit_succeeds(self, client, admin_user):
        """Cenário 4b: um login válido dentro do limite retorna 200."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'admin12345'
        })

        assert response.status_code == 200
        assert response.get_json()['success'] is True


class TestRegisterRateLimit:
    """POST /api/auth/register shares the strict auth limit (5 per minute)."""

    def test_register_exceeding_limit_returns_429_not_500(self, client):
        """Cenário 2: outra rota pública limitada também retorna 429 padronizado."""
        statuses = []
        for i in range(8):
            resp = client.post('/api/auth/register', json={
                'name': f'User {i}',
                'email': f'user{i}@test.com',
                'password': 'password12345'
            })
            statuses.append(resp.status_code)

        assert 429 in statuses, f"expected a 429, got {statuses}"
        assert 500 not in statuses, f"got a 500 (broken handler): {statuses}"
