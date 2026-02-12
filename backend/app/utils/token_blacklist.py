"""
Token Blacklist Management

Production-ready token blacklist using Redis with fallback to in-memory for development.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class TokenBlacklist:
    """
    Token blacklist manager with Redis support.

    In production, uses Redis for distributed token blacklist.
    In development/testing, falls back to in-memory storage.
    """

    def __init__(self):
        self._redis_client: Optional[object] = None
        self._memory_store: dict = {}
        self._initialized = False

    def init_app(self, app):
        """Initialize the token blacklist with Flask app context."""
        redis_url = app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')

        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self._redis_client.ping()
                logger.info("Token blacklist initialized with Redis")
            except ImportError:
                logger.warning("Redis package not installed. Using in-memory token blacklist.")
                self._redis_client = None
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory token blacklist.")
                self._redis_client = None
        else:
            env = os.environ.get('FLASK_ENV', 'development')
            if env == 'production':
                logger.warning(
                    "REDIS_URL not configured in production! "
                    "Token blacklist will not persist across restarts."
                )
            else:
                logger.info("Using in-memory token blacklist (development mode)")

        self._initialized = True

    def add(self, jti: str, expires_delta: Optional[timedelta] = None) -> bool:
        """
        Add a token JTI to the blacklist.

        Args:
            jti: The JWT ID to blacklist
            expires_delta: How long until the blacklist entry expires (defaults to 24 hours)

        Returns:
            True if successfully added, False otherwise
        """
        if expires_delta is None:
            expires_delta = timedelta(hours=24)

        expires_at = datetime.utcnow() + expires_delta

        if self._redis_client:
            try:
                # Use Redis with automatic expiration
                key = f"token_blacklist:{jti}"
                ttl_seconds = int(expires_delta.total_seconds())
                self._redis_client.setex(key, ttl_seconds, "revoked")
                return True
            except Exception as e:
                logger.error(f"Failed to add token to Redis blacklist: {e}")
                # Fallback to memory
                self._memory_store[jti] = expires_at
                return True
        else:
            # In-memory storage with expiration
            self._memory_store[jti] = expires_at
            self._cleanup_expired()
            return True

    def is_blacklisted(self, jti: str) -> bool:
        """
        Check if a token JTI is blacklisted.

        Args:
            jti: The JWT ID to check

        Returns:
            True if token is blacklisted, False otherwise
        """
        if self._redis_client:
            try:
                key = f"token_blacklist:{jti}"
                return self._redis_client.exists(key) > 0
            except Exception as e:
                logger.error(f"Failed to check Redis blacklist: {e}")
                # Fallback to memory check
                return self._check_memory(jti)
        else:
            return self._check_memory(jti)

    def _check_memory(self, jti: str) -> bool:
        """Check in-memory blacklist."""
        if jti not in self._memory_store:
            return False

        expires_at = self._memory_store[jti]
        if datetime.utcnow() > expires_at:
            # Token expired from blacklist, remove it
            del self._memory_store[jti]
            return False

        return True

    def _cleanup_expired(self):
        """Remove expired entries from in-memory store."""
        now = datetime.utcnow()
        expired_keys = [
            jti for jti, expires_at in self._memory_store.items()
            if now > expires_at
        ]
        for jti in expired_keys:
            del self._memory_store[jti]

    def revoke_all_user_tokens(self, user_id: str) -> bool:
        """
        Revoke all tokens for a specific user.

        Note: This requires storing user_id -> jti mappings,
        which is only available with Redis.

        Args:
            user_id: The user ID whose tokens should be revoked

        Returns:
            True if successful, False otherwise
        """
        if self._redis_client:
            try:
                # Find all tokens for this user
                pattern = f"user_tokens:{user_id}:*"
                keys = self._redis_client.keys(pattern)

                if keys:
                    # Get all JTIs and blacklist them
                    for key in keys:
                        jti = self._redis_client.get(key)
                        if jti:
                            self.add(jti)
                        self._redis_client.delete(key)

                return True
            except Exception as e:
                logger.error(f"Failed to revoke user tokens: {e}")
                return False
        else:
            logger.warning("Cannot revoke all user tokens without Redis")
            return False

    def register_token(self, jti: str, user_id: str, expires_delta: timedelta) -> bool:
        """
        Register a token for a user (enables revoke_all_user_tokens).

        Args:
            jti: The JWT ID
            user_id: The user ID
            expires_delta: Token expiration time

        Returns:
            True if successful, False otherwise
        """
        if self._redis_client:
            try:
                key = f"user_tokens:{user_id}:{jti}"
                ttl_seconds = int(expires_delta.total_seconds())
                self._redis_client.setex(key, ttl_seconds, jti)
                return True
            except Exception as e:
                logger.error(f"Failed to register token: {e}")
                return False
        return True  # No-op without Redis


# Singleton instance
token_blacklist = TokenBlacklist()
