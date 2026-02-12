"""
Users API Routes

Routes are protected with RBAC (Role-Based Access Control).
"""
import os
import uuid
from flask import Blueprint, request, g, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.services import UserService, UserSettingsService
from app.utils import (
    api_response,
    paginated_response,
    error_response,
    validate_json,
    validate_required_fields,
    validate_pagination
)
from app.utils.rbac import (
    require_auth,
    require_permission,
    require_self_or_admin,
    Permission
)

users_bp = Blueprint('users', __name__, url_prefix='/api')


# ============================================
# Users CRUD Routes
# ============================================

@users_bp.route('/users', methods=['GET'])
@require_auth
@validate_pagination
def get_users():
    """
    Get all users (requires authentication)

    Query params:
        - page: Page number (default: 1)
        - limit: Items per page (default: 50, max: 100)

    Response: PaginatedResponse<User[]>
    """
    page = request.pagination['page']
    limit = request.pagination['limit']

    users, total = UserService.get_all(page=page, limit=limit)

    return paginated_response(
        data=[u.to_dict() for u in users],
        page=page,
        limit=limit,
        total=total
    )


@users_bp.route('/users/<user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """
    Get a single user by ID (requires authentication)

    Response: ApiResponse<User>
    """
    user = UserService.get_by_id(user_id)

    if not user:
        return error_response('User not found', 404)

    return api_response(data=user.to_dict())


@users_bp.route('/users', methods=['POST'])
@require_permission(Permission.MANAGE_USERS)
@validate_json
@validate_required_fields(['name', 'email', 'password'])
def create_user():
    """
    Create a new user (Admin only)

    Body:
        - name: string (required)
        - email: string (required)
        - password: string (required)
        - role: string
        - department: string
        - phone: string
        - timezone: string

    Response: ApiResponse<User>
    """
    data = request.get_json()

    # Check if email already exists
    existing = UserService.get_by_email(data['email'])
    if existing:
        return error_response('A user with this email already exists', 409)

    try:
        user = UserService.create(data)
        return api_response(
            data=user.to_dict(),
            message='User created successfully',
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to create user: {str(e)}', 500)


# ============================================
# User Profile Routes (for current logged-in user)
# ============================================

@users_bp.route('/user/profile', methods=['GET'])
@require_auth
def get_current_user_profile():
    """
    Get current user's profile (from JWT token)

    Response: ApiResponse<UserProfile>
    """
    user_id = get_jwt_identity()

    profile = UserService.get_profile(user_id)

    if not profile:
        return error_response('User not found', 404)

    return api_response(data=profile)


@users_bp.route('/user/profile', methods=['PUT'])
@require_auth
@validate_json
def update_current_user_profile():
    """
    Update current user's profile (from JWT token)

    Body:
        - name: string
        - email: string
        - phone: string
        - department: string
        - timezone: string

    Response: ApiResponse<UserProfile>
    """
    user_id = get_jwt_identity()

    data = request.get_json()

    # Don't allow changing password or role through profile update
    data.pop('password', None)
    data.pop('role', None)

    try:
        user = UserService.update_profile(user_id, data)

        if not user:
            return error_response('User not found', 404)

        return api_response(
            data=user.to_profile_dict(),
            message='Profile updated successfully'
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to update profile: {str(e)}', 500)


# ============================================
# User Settings Routes
# ============================================

@users_bp.route('/user/settings', methods=['GET'])
@require_auth
def get_current_user_settings():
    """
    Get current user's settings (from JWT token)

    Response: ApiResponse<UserSettings>
    """
    user_id = get_jwt_identity()

    settings = UserSettingsService.get_by_user_id(user_id)

    if not settings:
        # Create default settings if not found
        settings = UserSettingsService.create_default(user_id)

    return api_response(data=settings.to_dict())


@users_bp.route('/user/settings', methods=['PUT'])
@require_auth
@validate_json
def update_current_user_settings():
    """
    Update current user's settings (from JWT token)

    Body:
        - theme: 'light' | 'dark' | 'system'
        - language: string
        - notifications: {
            email: boolean,
            push: boolean,
            taskReminders: boolean,
            projectUpdates: boolean
        }
        - displayPreferences: {
            compactMode: boolean,
            showAvatars: boolean,
            defaultView: 'gantt' | 'list' | 'board'
        }

    Response: ApiResponse<UserSettings>
    """
    user_id = get_jwt_identity()

    data = request.get_json()

    try:
        settings = UserSettingsService.update(user_id, data)

        if not settings:
            return error_response('Failed to update settings', 500)

        return api_response(
            data=settings.to_dict(),
            message='Settings updated successfully'
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to update settings: {str(e)}', 500)


# ============================================
# Avatar Upload Route
# ============================================

def _allowed_avatar_file(filename):
    """Check if file has an allowed extension"""
    allowed = current_app.config.get('ALLOWED_AVATAR_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@users_bp.route('/user/avatar', methods=['POST'])
@require_auth
def upload_avatar():
    """
    Upload user avatar image

    Accepts multipart/form-data with a 'file' field.
    Supported formats: png, jpg, jpeg, gif, webp
    Max size: 5MB (configured via MAX_CONTENT_LENGTH)

    Response: ApiResponse<UserProfile>
    """
    user_id = get_jwt_identity()

    if 'file' not in request.files:
        return error_response('No file provided', 400)

    file = request.files['file']

    if file.filename == '' or not file.filename:
        return error_response('No file selected', 400)

    if not _allowed_avatar_file(file.filename):
        return error_response('File type not allowed. Use: png, jpg, jpeg, gif, webp', 400)

    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        safe_filename = secure_filename(filename)

        # Save file
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        avatars_dir = os.path.join(upload_folder, 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)

        # Remove old avatar file if it exists locally
        user = UserService.get_by_id(user_id)
        if user and user.avatar and 'uploads/avatars/' in user.avatar:
            old_filename = user.avatar.split('uploads/avatars/')[-1]
            old_path = os.path.join(avatars_dir, old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)

        filepath = os.path.join(avatars_dir, safe_filename)
        file.save(filepath)

        # Build full URL for the avatar (needed because frontend runs on different port)
        avatar_url = f"{request.url_root}api/uploads/avatars/{safe_filename}"

        # Update user's avatar field
        updated_user = UserService.update(user_id, {'avatar': avatar_url})

        if not updated_user:
            return error_response('User not found', 404)

        return api_response(
            data=updated_user.to_profile_dict(),
            message='Avatar uploaded successfully'
        )
    except Exception as e:
        return error_response(f'Failed to upload avatar: {str(e)}', 500)


@users_bp.route('/uploads/avatars/<filename>', methods=['GET'])
def serve_avatar(filename):
    """Serve uploaded avatar files"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    avatars_dir = os.path.join(upload_folder, 'avatars')
    safe_name = secure_filename(filename)
    return send_from_directory(avatars_dir, safe_name)
