"""
Authentication API Routes

This module provides JWT authentication using flask-jwt-extended.
"""
from flask import Blueprint, request, current_app
from functools import wraps
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.services import UserService
from app.utils import api_response, error_response, validate_json, validate_required_fields
from app.utils.token_blacklist import token_blacklist
from app.utils.rate_limiter import rate_limit_auth, rate_limit_sensitive

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blacklist (Redis-backed in production)"""
    jti = jwt_payload["jti"]
    return token_blacklist.is_blacklisted(jti)


def get_current_user_id():
    """
    Get the current user ID from JWT token.
    """
    try:
        return get_jwt_identity()
    except Exception:
        return None


# ============================================
# Authentication Routes
# ============================================

@auth_bp.route('/login', methods=['POST'])
@rate_limit_auth
@validate_json
@validate_required_fields(['email', 'password'])
def login():
    """
    Authenticate user and return JWT tokens

    Body:
        - email: string (required)
        - password: string (required)

    Response: ApiResponse<{
        accessToken: string,
        refreshToken: string,
        user: User
    }>
    """
    data = request.get_json()

    user = UserService.authenticate(data['email'], data['password'])

    if not user:
        return error_response('Invalid email or password', 401)

    # Generate real JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return api_response(
        data={
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict()
        },
        message='Login successful'
    )


@auth_bp.route('/register', methods=['POST'])
@rate_limit_auth
@validate_json
@validate_required_fields(['name', 'email', 'password'])
def register():
    """
    Register a new user

    Body:
        - name: string (required)
        - email: string (required)
        - password: string (required)
        - role: string
        - department: string

    Response: ApiResponse<{
        accessToken: string,
        refreshToken: string,
        user: User
    }>
    """
    data = request.get_json()

    # Check if email already exists
    existing = UserService.get_by_email(data['email'])
    if existing:
        return error_response('A user with this email already exists', 409)

    # Validate password strength
    if len(data['password']) < 8:
        return error_response('Password must be at least 8 characters long', 400)

    try:
        user = UserService.create(data)

        # Generate real JWT tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return api_response(
            data={
                'accessToken': access_token,
                'refreshToken': refresh_token,
                'user': user.to_dict()
            },
            message='Registration successful',
            status_code=201
        )
    except Exception as e:
        return error_response(f'Failed to create user: {str(e)}', 500)


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using refresh token

    Headers:
        - Authorization: Bearer <refresh_token>

    Response: ApiResponse<{
        accessToken: string
    }>
    """
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return api_response(
        data={
            'accessToken': new_access_token
        },
        message='Token refreshed successfully'
    )


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (invalidate tokens)

    Adds the current token to the blacklist (Redis-backed in production).

    Response: ApiResponse<null>
    """
    jwt_data = get_jwt()
    jti = jwt_data['jti']

    # Get token expiration to set blacklist TTL
    exp_timestamp = jwt_data.get('exp')
    if exp_timestamp:
        from datetime import datetime, timedelta
        expires_at = datetime.fromtimestamp(exp_timestamp)
        expires_delta = expires_at - datetime.utcnow()
        if expires_delta.total_seconds() > 0:
            token_blacklist.add(jti, expires_delta)
        else:
            token_blacklist.add(jti)
    else:
        token_blacklist.add(jti)

    return api_response(
        data=None,
        message='Logged out successfully'
    )


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user

    Headers:
        - Authorization: Bearer <access_token>

    Response: ApiResponse<User>
    """
    user_id = get_jwt_identity()
    user = UserService.get_by_id(user_id)

    if not user:
        return error_response('User not found', 404)

    return api_response(data=user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@rate_limit_sensitive
@jwt_required()
@validate_json
@validate_required_fields(['currentPassword', 'newPassword'])
def change_password():
    """
    Change user password

    Body:
        - currentPassword: string (required)
        - newPassword: string (required)

    Response: ApiResponse<null>
    """
    data = request.get_json()
    user_id = get_jwt_identity()

    user = UserService.get_by_id(user_id)
    if not user:
        return error_response('User not found', 404)

    # Verify current password
    if not user.check_password(data['currentPassword']):
        return error_response('Current password is incorrect', 401)

    # Validate new password
    if len(data['newPassword']) < 8:
        return error_response('New password must be at least 8 characters long', 400)

    # Update password
    UserService.update(user_id, {'password': data['newPassword']})

    return api_response(
        data=None,
        message='Password changed successfully'
    )


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify if current token is valid

    Headers:
        - Authorization: Bearer <access_token>

    Response: ApiResponse<{ valid: boolean, userId: string }>
    """
    user_id = get_jwt_identity()

    return api_response(
        data={
            'valid': True,
            'userId': user_id
        },
        message='Token is valid'
    )
