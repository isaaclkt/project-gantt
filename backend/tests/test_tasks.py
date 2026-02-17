"""
Tests for task endpoints
"""
import pytest
from datetime import datetime, timedelta


class TestGetTasks:
    """Tests for GET /api/tasks"""

    def test_get_tasks_authenticated(self, client, admin_headers, sample_task):
        response = client.get('/api/tasks', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_get_tasks_unauthenticated(self, client):
        response = client.get('/api/tasks')

        assert response.status_code == 401

    def test_get_tasks_filter_by_project(self, client, admin_headers, sample_task, sample_project):
        response = client.get(
            f'/api/tasks?projectId={sample_project.id}',
            headers=admin_headers
        )
        data = response.get_json()

        assert response.status_code == 200
        for task in data['data']:
            assert task['projectId'] == sample_project.id

    def test_get_tasks_filter_by_status(self, client, admin_headers, sample_task):
        response = client.get('/api/tasks?status=todo', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        for task in data['data']:
            assert task['status'] == 'todo'

    def test_get_tasks_filter_by_priority(self, client, admin_headers, sample_task):
        response = client.get('/api/tasks?priority=medium', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        for task in data['data']:
            assert task['priority'] == 'medium'


class TestGetTask:
    """Tests for GET /api/tasks/<id>"""

    def test_get_task_by_id(self, client, admin_headers, sample_task):
        response = client.get(f'/api/tasks/{sample_task.id}', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['id'] == sample_task.id
        assert data['data']['name'] == 'Test Task'

    def test_get_task_not_found(self, client, admin_headers):
        response = client.get('/api/tasks/nonexistent', headers=admin_headers)

        assert response.status_code == 404


class TestCreateTask:
    """Tests for POST /api/tasks"""

    def test_create_task_as_member(self, client, member_headers, sample_project, team_member):
        today = datetime.now().date()
        response = client.post('/api/tasks', json={
            'name': 'New Task',
            'description': 'A new task',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=5)).isoformat(),
            'status': 'todo',
            'priority': 'high',
            'projectId': sample_project.id,
            'assigneeId': team_member.id
        }, headers=member_headers)
        data = response.get_json()

        assert response.status_code == 201
        assert data['data']['name'] == 'New Task'
        assert data['data']['priority'] == 'high'

    def test_create_task_as_viewer_forbidden(self, client, viewer_headers, sample_project):
        today = datetime.now().date()
        response = client.post('/api/tasks', json={
            'name': 'Forbidden Task',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=5)).isoformat(),
            'projectId': sample_project.id
        }, headers=viewer_headers)

        assert response.status_code == 403

    def test_create_task_missing_fields(self, client, member_headers):
        response = client.post('/api/tasks', json={
            'name': 'Incomplete Task'
        }, headers=member_headers)

        assert response.status_code == 400

    def test_create_task_invalid_status(self, client, member_headers, sample_project):
        today = datetime.now().date()
        response = client.post('/api/tasks', json={
            'name': 'Bad Status',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=5)).isoformat(),
            'projectId': sample_project.id,
            'status': 'invalid-status'
        }, headers=member_headers)

        assert response.status_code == 400


class TestDeleteTask:
    """Tests for DELETE /api/tasks/<id>"""

    def test_delete_task_as_admin(self, client, admin_headers, sample_task):
        response = client.delete(f'/api/tasks/{sample_task.id}', headers=admin_headers)

        assert response.status_code == 200

        # Verify it's gone
        get_resp = client.get(f'/api/tasks/{sample_task.id}', headers=admin_headers)
        assert get_resp.status_code == 404

    def test_delete_task_as_manager(self, client, manager_headers, sample_task):
        response = client.delete(f'/api/tasks/{sample_task.id}', headers=manager_headers)

        assert response.status_code == 200

    def test_delete_task_as_viewer_forbidden(self, client, viewer_headers, sample_task):
        response = client.delete(f'/api/tasks/{sample_task.id}', headers=viewer_headers)

        assert response.status_code == 403

    def test_delete_task_not_found(self, client, admin_headers):
        response = client.delete('/api/tasks/nonexistent', headers=admin_headers)

        assert response.status_code == 404


class TestTaskStatusUpdate:
    """Tests for PATCH /api/tasks/<id>/status"""

    def test_update_task_status(self, client, admin_headers, sample_task):
        response = client.patch(f'/api/tasks/{sample_task.id}/status', json={
            'status': 'in-progress'
        }, headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['status'] == 'in-progress'

    def test_update_task_invalid_status(self, client, admin_headers, sample_task):
        response = client.patch(f'/api/tasks/{sample_task.id}/status', json={
            'status': 'invalid'
        }, headers=admin_headers)

        assert response.status_code == 400


class TestTaskProgressUpdate:
    """Tests for PATCH /api/tasks/<id>/progress"""

    def test_update_task_progress(self, client, admin_headers, sample_task):
        response = client.patch(f'/api/tasks/{sample_task.id}/progress', json={
            'progress': 50
        }, headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['progress'] == 50

    def test_update_task_progress_invalid(self, client, admin_headers, sample_task):
        response = client.patch(f'/api/tasks/{sample_task.id}/progress', json={
            'progress': 150
        }, headers=admin_headers)

        assert response.status_code == 400

    def test_update_task_progress_negative(self, client, admin_headers, sample_task):
        response = client.patch(f'/api/tasks/{sample_task.id}/progress', json={
            'progress': -10
        }, headers=admin_headers)

        assert response.status_code == 400
