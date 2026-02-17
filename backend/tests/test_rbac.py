"""
Tests for Role-Based Access Control (RBAC)
"""
import pytest
from datetime import datetime, timedelta


class TestRolePermissions:
    """Test that roles have correct access levels"""

    def test_admin_can_access_all(self, client, admin_headers, sample_project, sample_task):
        # Can list projects
        assert client.get('/api/projects', headers=admin_headers).status_code == 200
        # Can create project
        today = datetime.now().date()
        assert client.post('/api/projects', json={
            'name': 'Admin Proj',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=admin_headers).status_code == 201
        # Can delete task (before project, since project delete may cascade)
        assert client.delete(f'/api/tasks/{sample_task.id}', headers=admin_headers).status_code == 200
        # Can delete project
        assert client.delete(f'/api/projects/{sample_project.id}', headers=admin_headers).status_code == 200

    def test_viewer_read_only(self, client, viewer_headers, sample_project, sample_task):
        today = datetime.now().date()

        # Can read projects
        assert client.get('/api/projects', headers=viewer_headers).status_code == 200
        # Can read single project
        assert client.get(f'/api/projects/{sample_project.id}', headers=viewer_headers).status_code == 200
        # Can read tasks
        assert client.get('/api/tasks', headers=viewer_headers).status_code == 200

        # Cannot create project
        resp = client.post('/api/projects', json={
            'name': 'Viewer Proj',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=viewer_headers)
        assert resp.status_code == 403

        # Cannot create task
        resp = client.post('/api/tasks', json={
            'name': 'Viewer Task',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=5)).isoformat(),
            'projectId': sample_project.id
        }, headers=viewer_headers)
        assert resp.status_code == 403

        # Cannot delete project
        assert client.delete(f'/api/projects/{sample_project.id}', headers=viewer_headers).status_code == 403

        # Cannot delete task
        assert client.delete(f'/api/tasks/{sample_task.id}', headers=viewer_headers).status_code == 403

    def test_member_can_create_tasks(self, client, member_headers, sample_project, team_member):
        today = datetime.now().date()
        resp = client.post('/api/tasks', json={
            'name': 'Member Task',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=5)).isoformat(),
            'projectId': sample_project.id,
            'assigneeId': team_member.id
        }, headers=member_headers)

        assert resp.status_code == 201

    def test_member_cannot_delete_projects(self, client, member_headers, sample_project):
        resp = client.delete(f'/api/projects/{sample_project.id}', headers=member_headers)

        assert resp.status_code == 403

    def test_manager_can_create_projects(self, client, manager_headers):
        today = datetime.now().date()
        resp = client.post('/api/projects', json={
            'name': 'Manager Proj',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=manager_headers)

        assert resp.status_code == 201

    def test_manager_can_delete_tasks(self, client, manager_headers, sample_task):
        resp = client.delete(f'/api/tasks/{sample_task.id}', headers=manager_headers)

        assert resp.status_code == 200


class TestUnauthenticatedAccess:
    """Test that unauthenticated requests are rejected"""

    def test_projects_requires_auth(self, client):
        assert client.get('/api/projects').status_code == 401

    def test_tasks_requires_auth(self, client):
        assert client.get('/api/tasks').status_code == 401

    def test_create_project_requires_auth(self, client):
        resp = client.post('/api/projects', json={'name': 'test'})
        assert resp.status_code == 401

    def test_create_task_requires_auth(self, client):
        resp = client.post('/api/tasks', json={'name': 'test'})
        assert resp.status_code == 401
