"""
Input Validation Utilities
"""
from functools import wraps
from flask import request
from app.utils.response import error_response


def validate_json(f):
    """Decorator to ensure request has valid JSON body"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return error_response('Content-Type must be application/json', 400)
        return f(*args, **kwargs)
    return decorated_function


def validate_required_fields(required_fields: list):
    """
    Decorator to validate required fields in request JSON

    Usage:
    @validate_required_fields(['name', 'email'])
    def create_user():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response('Content-Type must be application/json', 400)

            data = request.get_json()
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return error_response(
                    f'Missing required fields: {", ".join(missing_fields)}',
                    400,
                    {'missing_fields': missing_fields}
                )

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_enum_field(field_name: str, allowed_values: list):
    """
    Decorator to validate enum field values

    Usage:
    @validate_enum_field('status', ['todo', 'in-progress', 'review', 'completed'])
    def update_task():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if field_name in data and data[field_name] not in allowed_values:
                    return error_response(
                        f'Invalid value for {field_name}. Allowed values: {", ".join(allowed_values)}',
                        400
                    )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_pagination(f):
    """Decorator to validate and normalize pagination parameters"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))

            if page < 1:
                page = 1
            if limit < 1:
                limit = 10
            if limit > 100:
                limit = 100

            # Store in request context for use in route
            request.pagination = {'page': page, 'limit': limit}

        except ValueError:
            return error_response('Invalid pagination parameters', 400)

        return f(*args, **kwargs)
    return decorated_function


def validate_date_format(field_name: str):
    """
    Decorator to validate date format (YYYY-MM-DD)

    Usage:
    @validate_date_format('startDate')
    def create_task():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if field_name in data:
                    import re
                    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
                    if not re.match(date_pattern, data[field_name]):
                        return error_response(
                            f'Invalid date format for {field_name}. Expected format: YYYY-MM-DD',
                            400
                        )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_date_range(start_field: str = 'startDate', end_field: str = 'endDate'):
    """
    Decorator to validate that end date is after start date

    Usage:
    @validate_date_range('startDate', 'endDate')
    def create_project():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if start_field in data and end_field in data:
                    from datetime import datetime
                    try:
                        start_date = datetime.strptime(data[start_field], '%Y-%m-%d').date()
                        end_date = datetime.strptime(data[end_field], '%Y-%m-%d').date()

                        if end_date < start_date:
                            return error_response(
                                f'End date must be equal to or after start date',
                                400
                            )
                    except ValueError:
                        return error_response(
                            f'Invalid date format. Expected format: YYYY-MM-DD',
                            400
                        )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_progress(field_name: str = 'progress'):
    """
    Decorator to validate progress is between 0 and 100

    Usage:
    @validate_progress('progress')
    def update_task():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if field_name in data:
                    progress = data[field_name]
                    if not isinstance(progress, (int, float)):
                        return error_response(
                            f'{field_name} must be a number',
                            400
                        )
                    if progress < 0 or progress > 100:
                        return error_response(
                            f'{field_name} must be between 0 and 100',
                            400
                        )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_string_length(field_name: str, min_length: int = 0, max_length: int = 255):
    """
    Decorator to validate string length

    Usage:
    @validate_string_length('name', min_length=1, max_length=255)
    def create_project():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if field_name in data:
                    value = data[field_name]
                    if not isinstance(value, str):
                        return error_response(
                            f'{field_name} must be a string',
                            400
                        )
                    if len(value) < min_length:
                        return error_response(
                            f'{field_name} must be at least {min_length} characters',
                            400
                        )
                    if len(value) > max_length:
                        return error_response(
                            f'{field_name} must be at most {max_length} characters',
                            400
                        )
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_email(field_name: str = 'email'):
    """
    Decorator to validate email format

    Usage:
    @validate_email('email')
    def register():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                if field_name in data:
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, data[field_name]):
                        return error_response(
                            f'Invalid email format',
                            400
                        )
            return f(*args, **kwargs)
        return decorated_function
    return decorator
