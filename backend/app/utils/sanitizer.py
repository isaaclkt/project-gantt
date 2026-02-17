"""
Input Sanitization Utilities

Provides functions to sanitize user input and prevent XSS, SQL injection,
and other security vulnerabilities.
"""
import re
import html
from functools import wraps
from typing import Any, Dict, List, Optional, Union
from flask import request
import bleach


# Allowed HTML tags for rich text fields (if any)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}


def sanitize_string(value: str, max_length: Optional[int] = None, allow_html: bool = False) -> str:
    """
    Sanitize a string value.

    Args:
        value: The string to sanitize
        max_length: Maximum allowed length (truncates if exceeded)
        allow_html: If True, allows safe HTML tags; if False, strips all HTML

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return value

    # Strip leading/trailing whitespace
    value = value.strip()

    # Remove null bytes and other control characters (except newlines and tabs)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)

    if allow_html:
        # Clean HTML but allow safe tags
        value = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
    else:
        # Escape HTML entities
        value = html.escape(value)

    # Truncate if max_length specified
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def sanitize_email(email: str) -> str:
    """
    Sanitize an email address.

    Args:
        email: The email to sanitize

    Returns:
        Sanitized email (lowercase, stripped)
    """
    if not isinstance(email, str):
        return email

    # Strip whitespace and convert to lowercase
    email = email.strip().lower()

    # Remove any HTML/script tags
    email = bleach.clean(email, tags=[], strip=True)

    return email


def sanitize_integer(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Optional[int]:
    """
    Sanitize an integer value.

    Args:
        value: The value to sanitize
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        Sanitized integer or None if invalid
    """
    try:
        result = int(value)

        if min_val is not None and result < min_val:
            result = min_val
        if max_val is not None and result > max_val:
            result = max_val

        return result
    except (TypeError, ValueError):
        return None


def sanitize_dict(data: Dict[str, Any], schema: Dict[str, dict]) -> Dict[str, Any]:
    """
    Sanitize a dictionary based on a schema.

    Args:
        data: The dictionary to sanitize
        schema: Schema defining how to sanitize each field
            Example: {
                'name': {'type': 'string', 'max_length': 255},
                'email': {'type': 'email'},
                'description': {'type': 'string', 'allow_html': True},
                'priority': {'type': 'enum', 'values': ['low', 'medium', 'high']},
                'progress': {'type': 'integer', 'min': 0, 'max': 100}
            }

    Returns:
        Sanitized dictionary
    """
    result = {}

    for field, rules in schema.items():
        if field not in data:
            continue

        value = data[field]
        field_type = rules.get('type', 'string')

        if value is None:
            result[field] = None
            continue

        if field_type == 'string':
            result[field] = sanitize_string(
                value,
                max_length=rules.get('max_length'),
                allow_html=rules.get('allow_html', False)
            )
        elif field_type == 'email':
            result[field] = sanitize_email(value)
        elif field_type == 'integer':
            result[field] = sanitize_integer(
                value,
                min_val=rules.get('min'),
                max_val=rules.get('max')
            )
        elif field_type == 'enum':
            allowed = rules.get('values', [])
            result[field] = value if value in allowed else None
        elif field_type == 'boolean':
            result[field] = bool(value)
        elif field_type == 'date':
            # Validate date format YYYY-MM-DD
            if isinstance(value, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                result[field] = value
            else:
                result[field] = None
        else:
            # Unknown type, pass through with basic string sanitization
            if isinstance(value, str):
                result[field] = sanitize_string(value)
            else:
                result[field] = value

    return result


# Common schemas for reuse
USER_SCHEMA = {
    'name': {'type': 'string', 'max_length': 255},
    'email': {'type': 'email'},
    'password': {'type': 'string', 'max_length': 128},
    'role': {'type': 'string', 'max_length': 100},
    'department': {'type': 'string', 'max_length': 100},
}

PROJECT_SCHEMA = {
    'name': {'type': 'string', 'max_length': 255},
    'description': {'type': 'string', 'max_length': 2000, 'allow_html': False},
    'color': {'type': 'string', 'max_length': 7},  # Hex color
    'status': {'type': 'enum', 'values': ['planning', 'active', 'on-hold', 'completed', 'cancelled']},
    'progress': {'type': 'integer', 'min': 0, 'max': 100},
    'startDate': {'type': 'date'},
    'endDate': {'type': 'date'},
}

TASK_SCHEMA = {
    'name': {'type': 'string', 'max_length': 255},
    'description': {'type': 'string', 'max_length': 2000, 'allow_html': False},
    'status': {'type': 'enum', 'values': ['todo', 'in-progress', 'review', 'completed']},
    'priority': {'type': 'enum', 'values': ['low', 'medium', 'high', 'critical']},
    'progress': {'type': 'integer', 'min': 0, 'max': 100},
    'startDate': {'type': 'date'},
    'endDate': {'type': 'date'},
}


def sanitize_request_data(schema: Dict[str, dict]):
    """
    Decorator to sanitize request JSON data based on a schema.

    Usage:
        @sanitize_request_data(PROJECT_SCHEMA)
        def create_project():
            data = request.get_json()  # Data is already sanitized
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                original_data = request.get_json()
                if original_data:
                    sanitized = sanitize_dict(original_data, schema)
                    # Store sanitized data for the route to use
                    request.sanitized_data = sanitized
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_sanitized_data() -> Dict[str, Any]:
    """
    Get sanitized request data.

    Returns:
        Sanitized data dictionary or empty dict if not available
    """
    return getattr(request, 'sanitized_data', {})
