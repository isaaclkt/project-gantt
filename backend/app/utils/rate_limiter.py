"""
Rate Limiting Configuration

Provides rate limiting for API endpoints using Flask-Limiter.
Uses Redis in production for distributed rate limiting.
"""
import os
import logging
from functools import wraps
from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)


def get_request_identifier():
    """
    Get identifier for rate limiting.

    Uses authenticated user ID if available, otherwise falls back to IP address.
    This prevents authenticated users from being affected by other users on the same IP.
    """
    # Try to get user ID from JWT if authenticated
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return f"user:{user_id}"
    except Exception:
        pass

    # Fallback to IP address
    return get_remote_address()


# Create limiter instance
limiter = Limiter(
    key_func=get_request_identifier,
    default_limits=["200 per minute"],
    storage_uri=os.environ.get('REDIS_URL', 'memory://'),
    strategy="fixed-window",
    headers_enabled=True
)


# Custom rate limit decorators for different endpoint types
def rate_limit_auth(f):
    """
    Strict rate limit for authentication endpoints.
    Prevents brute force attacks on login/register.
    """
    @wraps(f)
    @limiter.limit("5 per minute", key_func=get_remote_address)
    @limiter.limit("20 per hour", key_func=get_remote_address)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def rate_limit_api(limit: str = "60 per minute"):
    """
    Standard rate limit for API endpoints.

    Args:
        limit: Rate limit string (e.g., "60 per minute", "1000 per hour")
    """
    def decorator(f):
        @wraps(f)
        @limiter.limit(limit)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit_write(f):
    """
    Rate limit for write operations (POST, PUT, DELETE).
    More restrictive than read operations.
    """
    @wraps(f)
    @limiter.limit("30 per minute")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def rate_limit_sensitive(f):
    """
    Very strict rate limit for sensitive operations.
    E.g., password changes, account deletion.
    """
    @wraps(f)
    @limiter.limit("3 per minute", key_func=get_remote_address)
    @limiter.limit("10 per hour", key_func=get_remote_address)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


# Error handler for rate limit exceeded
def rate_limit_exceeded_handler(e):
    """
    Handle rate limit exceeded (HTTP 429) errors.

    Returns the API's standard error payload
    ({data: null, success: false, message, errors?}) via the shared
    error_response() helper, so a throttled request looks exactly like any
    other API error to the client instead of blowing up into a 500.
    """
    from app.utils.response import error_response

    logger.warning(
        f"Rate limit exceeded: {get_remote_address()} - {request.endpoint}"
    )

    # Flask-Limiter sets e.description to the limit that was hit (e.g.
    # "5 per 1 minute"). It is NOT a number of seconds, so we expose it as
    # context under `errors`, never as a bogus retry_after value.
    limit_info = getattr(e, 'description', None)
    errors = {'limit': limit_info} if limit_info else None

    response, status_code = error_response(
        message="Muitas requisições. Tente novamente em instantes.",
        status_code=429,
        errors=errors,
    )

    # Preserve the Retry-After header when Flask-Limiter provides it, so the
    # client knows how long to back off before retrying.
    retry_after = getattr(e, 'retry_after', None)
    if retry_after is not None:
        response.headers['Retry-After'] = str(retry_after)

    return response, status_code
