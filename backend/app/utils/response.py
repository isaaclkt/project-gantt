"""
API Response Utilities
"""
from flask import jsonify
from typing import Any, Optional


def api_response(
    data: Any = None,
    success: bool = True,
    message: Optional[str] = None,
    status_code: int = 200
):
    """
    Create a standardized API response matching frontend ApiResponse<T> type

    Format:
    {
        "data": T,
        "success": boolean,
        "message": string (optional)
    }
    """
    response = {
        'data': data,
        'success': success
    }

    if message:
        response['message'] = message

    return jsonify(response), status_code


def paginated_response(
    data: Any,
    page: int,
    limit: int,
    total: int,
    message: Optional[str] = None
):
    """
    Create a standardized paginated API response matching frontend PaginatedResponse<T> type

    Format:
    {
        "data": T,
        "success": boolean,
        "message": string (optional),
        "pagination": {
            "page": number,
            "limit": number,
            "total": number,
            "totalPages": number
        }
    }
    """
    total_pages = (total + limit - 1) // limit if limit > 0 else 0

    response = {
        'data': data,
        'success': True,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'totalPages': total_pages
        }
    }

    if message:
        response['message'] = message

    return jsonify(response), 200


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[dict] = None
):
    """
    Create a standardized error response

    Format:
    {
        "data": null,
        "success": false,
        "message": string,
        "errors": dict (optional, for validation errors)
    }
    """
    response = {
        'data': None,
        'success': False,
        'message': message
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status_code
