"""
Tests for project endpoints
"""
import pytest
from datetime import datetime, timedelta


class TestGetProjects:
    """Tests for GET /api/projects"""

    def test_get_projects_authenticated(self, client, admin_headers, sample_project):
        response = client.get('/api/projects', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_get_projects_unauthenticated(self, client):
        response = client.get('/api/projects')

        assert response.status_code == 401

    def test_get_projects_filter_by_status(self, client, admin_headers, sample_project):
        response = client.get('/api/projects?status=active', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        for project in data['data']:
            assert project['status'] == 'active'


class TestGetProject:
    """Tests for GET /api/projects/<id>"""

    def test_get_project_by_id(self, client, admin_headers, sample_project):
        response = client.get(f'/api/projects/{sample_project.id}', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['id'] == sample_project.id
        assert data['data']['name'] == 'Test Project'

    def test_get_project_not_found(self, client, admin_headers):
        response = client.get('/api/projects/nonexistent', headers=admin_headers)

        assert response.status_code == 404


class TestCreateProject:
    """Tests for POST /api/projects"""

    def test_create_project_as_manager(self, client, manager_headers):
        today = datetime.now().date()
        response = client.post('/api/projects', json={
            'name': 'New Project',
            'description': 'A new project',
            'color': '#FF5733',
            'status': 'planning',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=30)).isoformat()
        }, headers=manager_headers)
        data = response.get_json()

        assert response.status_code == 201
        assert data['data']['name'] == 'New Project'

    def test_create_project_as_admin(self, client, admin_headers):
        today = datetime.now().date()
        response = client.post('/api/projects', json={
            'name': 'Admin Project',
            'description': 'Created by admin',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=admin_headers)

        assert response.status_code == 201

    def test_create_project_as_viewer_forbidden(self, client, viewer_headers):
        today = datetime.now().date()
        response = client.post('/api/projects', json={
            'name': 'Forbidden Project',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=viewer_headers)

        assert response.status_code == 403

    def test_create_project_missing_fields(self, client, manager_headers):
        response = client.post('/api/projects', json={
            'name': 'Incomplete'
        }, headers=manager_headers)

        assert response.status_code == 400

    def test_create_project_invalid_dates(self, client, manager_headers):
        today = datetime.now().date()
        response = client.post('/api/projects', json={
            'name': 'Bad Dates',
            'startDate': (today + timedelta(days=10)).isoformat(),
            'endDate': today.isoformat()
        }, headers=manager_headers)

        assert response.status_code == 400


class TestUpdateProject:
    """Tests for PUT /api/projects/<id>"""

    def test_update_project_as_admin(self, client, admin_headers, sample_project):
        response = client.put(f'/api/projects/{sample_project.id}', json={
            'name': 'Updated Project Name',
            'progress': 75
        }, headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert data['data']['name'] == 'Updated Project Name'

    def test_update_project_not_found(self, client, admin_headers):
        response = client.put('/api/projects/nonexistent', json={
            'name': 'Ghost'
        }, headers=admin_headers)

        assert response.status_code == 404


class TestDeleteProject:
    """Tests for DELETE /api/projects/<id>"""

    def test_delete_project_as_admin(self, client, admin_headers, sample_project):
        response = client.delete(f'/api/projects/{sample_project.id}', headers=admin_headers)

        assert response.status_code == 200

        # Verify it's gone
        get_resp = client.get(f'/api/projects/{sample_project.id}', headers=admin_headers)
        assert get_resp.status_code == 404

    def test_delete_project_as_viewer_forbidden(self, client, viewer_headers, sample_project):
        response = client.delete(f'/api/projects/{sample_project.id}', headers=viewer_headers)

        assert response.status_code == 403

    def test_delete_project_not_found(self, client, admin_headers):
        response = client.delete('/api/projects/nonexistent', headers=admin_headers)

        assert response.status_code == 404


class TestProjectMembers:
    """Tests for project member management"""

    def test_get_project_members(self, client, admin_headers, sample_project):
        response = client.get(f'/api/projects/{sample_project.id}/members', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert isinstance(data['data'], list)

    def test_add_member_to_project(self, client, admin_headers, sample_project, team_member):
        response = client.post(
            f'/api/projects/{sample_project.id}/members/{team_member.id}',
            headers=admin_headers
        )

        assert response.status_code == 200

    def test_get_project_tasks(self, client, admin_headers, sample_project, sample_task):
        response = client.get(f'/api/projects/{sample_project.id}/tasks', headers=admin_headers)
        data = response.get_json()

        assert response.status_code == 200
        assert len(data['data']) >= 1
