"""
Tests for department scoping of the `department_admin` role.

A `department_admin` administers a single department. It must never see
projects/tasks that belong to other departments — not in listings, not in the
insights aggregation. `admin` remains global. Other roles keep their existing
(non department-scoped) visibility.

A project's department is derived from its owner's department_id (the system's
source of truth, also used by check_project_department_scope). Tasks inherit the
department from their project.
"""
import pytest
from datetime import datetime, timedelta

from app.models.user import User, UserSettings
from app.models.department import Department
from app.models.project import Project
from app.models.task import Task
from app.models.team_member import TeamMember
from flask_jwt_extended import create_access_token


# ---------------------------------------------------------------------------
# Fixtures: two departments, each with an owner, a project and a task.
# ---------------------------------------------------------------------------

@pytest.fixture
def two_departments(db_session):
    """Create dept A and dept B."""
    dept_a = Department(id='dept-a', name='Engineering')
    dept_b = Department(id='dept-b', name='Marketing')
    db_session.session.add_all([dept_a, dept_b])
    db_session.session.commit()
    return dept_a, dept_b


@pytest.fixture
def dept_a_admin(db_session, two_departments):
    """A department_admin scoped to department A."""
    dept_a, _ = two_departments
    user = User(
        id='dadmin-a',
        name='Dept A Admin',
        email='dadmin-a@test.com',
        role='department_admin',
        department_id=dept_a.id,
        department='Engineering'
    )
    user.set_password('password12345')
    db_session.session.add(user)
    db_session.session.add(UserSettings(user_id=user.id))
    db_session.session.commit()
    return user


@pytest.fixture
def dept_a_owner(db_session, two_departments):
    """A manager in department A who owns dept-A projects."""
    dept_a, _ = two_departments
    user = User(
        id='owner-a', name='Owner A', email='owner-a@test.com',
        role='manager', department_id=dept_a.id, department='Engineering'
    )
    user.set_password('password12345')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def dept_b_owner(db_session, two_departments):
    """A manager in department B who owns dept-B projects."""
    _, dept_b = two_departments
    user = User(
        id='owner-b', name='Owner B', email='owner-b@test.com',
        role='manager', department_id=dept_b.id, department='Marketing'
    )
    user.set_password('password12345')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def project_a(db_session, dept_a_owner):
    today = datetime.now().date()
    p = Project(
        id='proj-a', name='Project A', status='active', progress=10,
        start_date=today - timedelta(days=5), end_date=today + timedelta(days=15),
        owner_id=dept_a_owner.id
    )
    db_session.session.add(p)
    db_session.session.commit()
    return p


@pytest.fixture
def project_b(db_session, dept_b_owner):
    today = datetime.now().date()
    p = Project(
        id='proj-b', name='Project B', status='active', progress=20,
        start_date=today - timedelta(days=5), end_date=today + timedelta(days=15),
        owner_id=dept_b_owner.id
    )
    db_session.session.add(p)
    db_session.session.commit()
    return p


@pytest.fixture
def task_a(db_session, project_a):
    today = datetime.now().date()
    t = Task(
        id='task-a', name='Task A', start_date=today,
        end_date=today + timedelta(days=5), status='todo', priority='medium',
        progress=0, project_id=project_a.id
    )
    db_session.session.add(t)
    db_session.session.commit()
    return t


@pytest.fixture
def task_b(db_session, project_b):
    today = datetime.now().date()
    t = Task(
        id='task-b', name='Task B', start_date=today,
        end_date=today + timedelta(days=5), status='todo', priority='high',
        progress=0, project_id=project_b.id
    )
    db_session.session.add(t)
    db_session.session.commit()
    return t


def _headers(app, user_id):
    with app.app_context():
        token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def dept_a_admin_headers(app, dept_a_admin):
    return _headers(app, dept_a_admin.id)


# ---------------------------------------------------------------------------
# Cenário 1 — department_admin listing projects
# ---------------------------------------------------------------------------

class TestProjectListingScope:

    def test_dept_admin_sees_only_own_department_projects(
        self, client, dept_a_admin_headers, project_a, project_b
    ):
        response = client.get('/api/projects', headers=dept_a_admin_headers)
        assert response.status_code == 200

        ids = {p['id'] for p in response.get_json()['data']}
        assert 'proj-a' in ids
        assert 'proj-b' not in ids

    def test_admin_sees_all_projects(
        self, client, admin_headers, project_a, project_b
    ):
        response = client.get('/api/projects', headers=admin_headers)
        assert response.status_code == 200

        ids = {p['id'] for p in response.get_json()['data']}
        assert {'proj-a', 'proj-b'}.issubset(ids)

    def test_dept_admin_without_department_sees_nothing(
        self, client, app, db_session, project_a, project_b
    ):
        """Fail closed: a department_admin with no department gets an empty list."""
        user = User(
            id='dadmin-none', name='No Dept Admin', email='none@test.com',
            role='department_admin', department_id=None
        )
        user.set_password('password12345')
        db_session.session.add(user)
        db_session.session.commit()

        response = client.get('/api/projects', headers=_headers(app, user.id))
        assert response.status_code == 200
        assert response.get_json()['data'] == []


# ---------------------------------------------------------------------------
# Cenário 2 — department_admin listing tasks
# ---------------------------------------------------------------------------

class TestTaskListingScope:

    def test_dept_admin_sees_only_own_department_tasks(
        self, client, dept_a_admin_headers, task_a, task_b
    ):
        response = client.get('/api/tasks', headers=dept_a_admin_headers)
        assert response.status_code == 200

        ids = {t['id'] for t in response.get_json()['data']}
        assert 'task-a' in ids
        assert 'task-b' not in ids

    def test_admin_sees_all_tasks(self, client, admin_headers, task_a, task_b):
        response = client.get('/api/tasks', headers=admin_headers)
        assert response.status_code == 200

        ids = {t['id'] for t in response.get_json()['data']}
        assert {'task-a', 'task-b'}.issubset(ids)


# ---------------------------------------------------------------------------
# Cenário 3 — department_admin accessing cross-department detail
# ---------------------------------------------------------------------------

class TestCrossDepartmentDetail:

    def test_dept_admin_cannot_read_other_department_project(
        self, client, dept_a_admin_headers, project_b
    ):
        response = client.get('/api/projects/proj-b', headers=dept_a_admin_headers)
        assert response.status_code == 403

    def test_dept_admin_can_read_own_department_project(
        self, client, dept_a_admin_headers, project_a
    ):
        response = client.get('/api/projects/proj-a', headers=dept_a_admin_headers)
        assert response.status_code == 200
        assert response.get_json()['data']['id'] == 'proj-a'

    def test_dept_admin_cannot_read_other_department_task(
        self, client, dept_a_admin_headers, task_b
    ):
        response = client.get('/api/tasks/task-b', headers=dept_a_admin_headers)
        assert response.status_code == 403

    def test_dept_admin_can_read_own_department_task(
        self, client, dept_a_admin_headers, task_a
    ):
        response = client.get('/api/tasks/task-a', headers=dept_a_admin_headers)
        assert response.status_code == 200
        assert response.get_json()['data']['id'] == 'task-a'


# ---------------------------------------------------------------------------
# Insights aggregation must also be department-scoped
# ---------------------------------------------------------------------------

class TestInsightsScope:

    def test_dept_admin_insights_exclude_other_department(
        self, client, dept_a_admin_headers, task_a, task_b
    ):
        """
        task_b is a high-priority, unassigned task in dept B. A dept-A admin's
        insights must not surface it (it would appear as an unassigned
        high-priority critical insight if the data leaked).
        """
        response = client.get('/api/insights', headers=dept_a_admin_headers)
        assert response.status_code == 200

        blob = str(response.get_json()['data'])
        assert 'Task B' not in blob
        # Sanity: dept-A task is medium priority, so it should not appear in the
        # high-priority-unassigned insight either — but the aggregation ran
        # without error and produced a summary.
        assert response.get_json()['data']['insights'] is not None

    def test_admin_insights_include_all_departments(
        self, client, admin_headers, task_a, task_b
    ):
        response = client.get('/api/insights', headers=admin_headers)
        assert response.status_code == 200
        blob = str(response.get_json()['data'])
        # The unassigned high-priority dept-B task should surface for a global admin.
        assert 'Task B' in blob


# ---------------------------------------------------------------------------
# Explicit Project.department_id is the source of truth (not the owner)
# ---------------------------------------------------------------------------

class TestExplicitProjectDepartment:

    def test_explicit_department_overrides_owner(
        self, client, dept_a_admin_headers, db_session, dept_b_owner, two_departments
    ):
        """
        A project owned by a dept-B user but explicitly tagged to dept A must be
        visible to the dept-A admin — the explicit column wins over the owner.
        """
        dept_a, _ = two_departments
        today = datetime.now().date()
        p = Project(
            id='proj-mixed', name='Mixed Project', status='active', progress=0,
            start_date=today - timedelta(days=1), end_date=today + timedelta(days=10),
            owner_id=dept_b_owner.id,          # owner is in dept B
            department_id=dept_a.id            # but explicitly assigned to dept A
        )
        db_session.session.add(p)
        db_session.session.commit()

        # Listing: dept-A admin sees it.
        listing = client.get('/api/projects', headers=dept_a_admin_headers)
        ids = {x['id'] for x in listing.get_json()['data']}
        assert 'proj-mixed' in ids

        # Detail: dept-A admin is allowed, response echoes the department.
        detail = client.get('/api/projects/proj-mixed', headers=dept_a_admin_headers)
        assert detail.status_code == 200
        assert detail.get_json()['data']['departmentId'] == dept_a.id

    def test_create_inherits_owner_department(
        self, client, app, db_session, two_departments
    ):
        """Creating a project without an explicit department inherits the owner's."""
        dept_a, _ = two_departments
        creator = User(
            id='mgr-a', name='Manager A', email='mgr-a@test.com',
            role='manager', department_id=dept_a.id
        )
        creator.set_password('password12345')
        db_session.session.add(creator)
        db_session.session.commit()

        today = datetime.now().date()
        response = client.post('/api/projects', json={
            'name': 'Inherited Dept Project',
            'startDate': today.isoformat(),
            'endDate': (today + timedelta(days=10)).isoformat()
        }, headers=_headers(app, creator.id))

        assert response.status_code == 201
        assert response.get_json()['data']['departmentId'] == dept_a.id
