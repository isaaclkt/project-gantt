"""
Application Configuration Settings
"""
import os
import secrets
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()

logger = logging.getLogger(__name__)


def _get_secret_key(env_var: str, default_dev_value: str) -> str:
    """
    Get secret key from environment or generate a secure random one.

    In production, raises an error if the secret is not explicitly set.
    In development, uses a random key if not set (with a warning).
    """
    value = os.environ.get(env_var)
    env = os.environ.get('FLASK_ENV', 'development')

    if value and value not in [default_dev_value, 'dev-secret-key-change-in-production',
                                'jwt-secret-key-change-in-production']:
        return value

    if env == 'production':
        raise ValueError(
            f"SECURITY ERROR: {env_var} must be set to a secure random value in production! "
            f"Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Development/testing: generate random key and warn
    random_key = secrets.token_hex(32)
    logger.warning(
        f"{env_var} not set. Using random key for this session. "
        f"Set {env_var} in .env for consistent sessions across restarts."
    )
    return random_key


class Config:
    """Base configuration"""

    # Flask - Secure secret key handling
    SECRET_KEY = _get_secret_key('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/project_grantt'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JWT Configuration - Secure secret key handling
    JWT_SECRET_KEY = _get_secret_key('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # Redis (for token blacklist and rate limiting)
    REDIS_URL = os.environ.get('REDIS_URL')

    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = '200 per minute'
    RATELIMIT_HEADERS_ENABLED = True

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max
    ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Stricter rate limits for production
    RATELIMIT_DEFAULT = '100 per minute'

    @classmethod
    def init_app(cls, app):
        """Production-specific initialization"""
        import logging
        from logging.handlers import RotatingFileHandler

        # Validate critical production settings
        cls._validate_production_config()

        # Setup logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')

    @classmethod
    def _validate_production_config(cls):
        """Validate that all required production settings are configured."""
        errors = []

        # Check for required environment variables
        if not os.environ.get('SECRET_KEY'):
            errors.append("SECRET_KEY must be set in production")

        if not os.environ.get('JWT_SECRET_KEY'):
            errors.append("JWT_SECRET_KEY must be set in production")

        if not os.environ.get('DATABASE_URL'):
            errors.append("DATABASE_URL must be set in production")

        # Warn about missing Redis (not fatal, but recommended)
        if not os.environ.get('REDIS_URL'):
            logger.warning(
                "REDIS_URL not set in production. Token blacklist and rate limiting "
                "will use in-memory storage (not recommended for multi-instance deployments)"
            )

        # Check CORS origins
        cors_origins = os.environ.get('CORS_ORIGINS', '')
        if 'localhost' in cors_origins or '127.0.0.1' in cors_origins:
            logger.warning(
                "CORS_ORIGINS contains localhost in production. "
                "Consider restricting to production domains only."
            )

        if errors:
            raise ValueError(
                "Production configuration errors:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
