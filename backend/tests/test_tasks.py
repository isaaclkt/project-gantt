"""
Tests for task endpoints
"""
import pytest
from datetime import datetime, timedelta
from app.models import TeamMember, Task


@pytest.fixture
def viewer_as_project_member(db_session, viewer_user, sample_project):
    """
    Link the viewer to sample_project as a team member.

    This gives the viewer legitimate READ access to the project's tasks
    (is_project_member is True) — the exact situation that previously let a
    viewer slip through the write endpoints.
    """
    tm = TeamMember(
        id='tm-viewer',
        user_id=viewer_user.id,
        name=viewer_user.name,
        email=viewer_user.email,
        role='Viewer',
        department='External',
        status='active'
    )
    db_session.session.add(tm)
    sample_project.team_members.append(tm)
    db_session.session.commit()
    return tm


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


class TestViewerTaskWriteAccess:
    """
    A 'viewer' is read-only. Even when the viewer legitimately participates in
    the project (and could therefore READ the task), they must never be able to
    modify it (update / status / progress / delete).
    """

    # --- Cenario 1: viewer CAN read ---

    def test_viewer_can_read_task_list(self, client, viewer_headers, sample_task):
        assert client.get('/api/tasks', headers=viewer_headers).status_code == 200

    def test_viewer_member_can_read_single_task(
        self, client, viewer_headers, sample_task, viewer_as_project_member
    ):
        response = client.get(f'/api/tasks/{sample_task.id}', headers=viewer_headers)
        assert response.status_code == 200
        assert response.get_json()['data']['id'] == sample_task.id

    # --- Cenario 2: viewer CANNOT edit ---

    def test_viewer_member_cannot_update_task(
        self, client, viewer_headers, sample_task, viewer_as_project_member
    ):
        response = client.put(
            f'/api/tasks/{sample_task.id}',
            json={'name': 'Hacked by viewer'},
            headers=viewer_headers
        )
        assert response.status_code == 403

    # --- Cenario 3: viewer CANNOT change status/progress ---

    def test_viewer_member_cannot_update_status(
        self, client, viewer_headers, sample_task, viewer_as_project_member
    ):
        response = client.patch(
            f'/api/tasks/{sample_task.id}/status',
            json={'status': 'completed'},
            headers=viewer_headers
        )
        assert response.status_code == 403

    def test_viewer_member_cannot_update_progress(
        self, client, viewer_headers, sample_task, viewer_as_project_member
    ):
        response = client.patch(
            f'/api/tasks/{sample_task.id}/progress',
            json={'progress': 100},
            headers=viewer_headers
        )
        assert response.status_code == 403

    # --- Cenario 4: viewer CANNOT delete ---

    def test_viewer_member_cannot_delete_task(
        self, client, viewer_headers, sample_task, viewer_as_project_member
    ):
        response = client.delete(f'/api/tasks/{sample_task.id}', headers=viewer_headers)
        assert response.status_code == 403

    # --- Strongest case: even a viewer who is the ASSIGNEE is blocked ---

    def test_viewer_assignee_still_cannot_update(
        self, client, db_session, viewer_user, viewer_headers, sample_project
    ):
        today = datetime.now().date()
        tm = TeamMember(
            id='tm-viewer-assignee',
            user_id=viewer_user.id,
            name=viewer_user.name,
            email=viewer_user.email,
            role='Viewer',
            status='active'
        )
        db_session.session.add(tm)
        task = Task(
            id='task-viewer-assigned',
            name='Assigned to viewer',
            start_date=today,
            end_date=today + timedelta(days=3),
            status='todo',
            priority='medium',
            progress=0,
            assignee_id='tm-viewer-assignee',
            project_id=sample_project.id
        )
        db_session.session.add(task)
        db_session.session.commit()

        response = client.put(
            f'/api/tasks/{task.id}',
            json={'progress': 100, 'status': 'completed'},
            headers=viewer_headers
        )
        assert response.status_code == 403

    # --- Cenario 5: an authorized role CAN still edit (no over-block) ---

    def test_member_assignee_can_update_task(self, client, member_headers, sample_task):
        response = client.put(
            f'/api/tasks/{sample_task.id}',
            json={'name': 'Updated by member'},
            headers=member_headers
        )
        assert response.status_code == 200
        assert response.get_json()['data']['name'] == 'Updated by member'

    def test_manager_can_update_task_status(self, client, manager_headers, sample_task):
        response = client.patch(
            f'/api/tasks/{sample_task.id}/status',
            json={'status': 'in-progress'},
            headers=manager_headers
        )
        assert response.status_code == 200
        assert response.get_json()['data']['status'] == 'in-progress'
