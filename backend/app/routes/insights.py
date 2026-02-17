"""
Insights API Routes

Provides smart analysis of projects, tasks, and team data.
"""
from datetime import datetime
from flask import Blueprint
from app.services import InsightsService
from app.utils import api_response, error_response
from app.utils.rbac import require_auth

insights_bp = Blueprint('insights', __name__, url_prefix='/api/insights')


@insights_bp.route('', methods=['GET'])
@require_auth
def get_insights():
    """
    Get smart insights about projects, tasks, and team.

    Analyzes all data and returns categorized insights:
    - critical: overdue tasks, overdue projects, unassigned high-priority
    - warning: due soon, overloaded members, behind schedule
    - positive: completed tasks, on-track projects, top performers
    - info: summary stats

    Response: ApiResponse<{ insights: Insight[], generatedAt: string }>
    """
    try:
        insights = InsightsService.generate()

        return api_response(data={
            'insights': insights,
            'generatedAt': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return error_response(f'Failed to generate insights: {str(e)}', 500)
