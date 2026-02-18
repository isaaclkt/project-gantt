"""
Database Seed Script
Creates test users and sample data for ProjectFlow
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config.database import db
from app.models.user import User, UserSettings
from app.models.team_member import TeamMember
from app.models.department import Department, Role
from app.models.project import Project
from app.models.task import Task
from datetime import datetime, timedelta
import uuid


def create_departments():
    """Create sample departments"""
    departments = [
        {'name': 'Tecnologia', 'description': 'Desenvolvimento e infraestrutura'},
        {'name': 'Design', 'description': 'UI/UX e Design Gráfico'},
        {'name': 'Marketing', 'description': 'Marketing e Comunicação'},
        {'name': 'Gestão', 'description': 'Gerenciamento de Projetos'},
        {'name': 'Qualidade', 'description': 'QA e Testes'},
    ]

    created = []
    for dept in departments:
        d = Department(
            id=str(uuid.uuid4()),
            name=dept['name'],
            description=dept['description']
        )
        db.session.add(d)
        created.append(d)

    db.session.commit()
    print(f"[OK] Created {len(created)} departments")
    return created


def create_roles():
    """Create sample job roles"""
    roles = [
        {'name': 'Desenvolvedor Frontend', 'description': 'Desenvolvimento de interfaces'},
        {'name': 'Desenvolvedor Backend', 'description': 'Desenvolvimento de APIs'},
        {'name': 'Designer UI/UX', 'description': 'Design de interfaces'},
        {'name': 'Gerente de Projetos', 'description': 'Gestão de projetos'},
        {'name': 'Analista de QA', 'description': 'Garantia de qualidade'},
        {'name': 'DevOps', 'description': 'Infraestrutura e deploy'},
    ]

    created = []
    for role in roles:
        r = Role(
            id=str(uuid.uuid4()),
            name=role['name'],
            description=role['description']
        )
        db.session.add(r)
        created.append(r)

    db.session.commit()
    print(f"[OK] Created {len(created)} job roles")
    return created


def create_test_users(departments):
    """Create test users with different access levels"""

    tech_dept = next((d for d in departments if d.name == 'Tecnologia'), None)

    users_data = [
        {
            'name': 'Administrador',
            'email': 'admin@projectflow.com',
            'password': 'admin123',
            'role': 'admin',
            'department': 'Gestão',
        },
        {
            'name': 'Gerente de Projetos',
            'email': 'gerente@projectflow.com',
            'password': 'gerente123',
            'role': 'manager',
            'department': 'Gestão',
        },
        {
            'name': 'João Desenvolvedor',
            'email': 'membro@projectflow.com',
            'password': 'membro123',
            'role': 'member',
            'department': 'Tecnologia',
            'department_id': tech_dept.id if tech_dept else None,
        },
        {
            'name': 'Maria Visualizadora',
            'email': 'viewer@projectflow.com',
            'password': 'viewer123',
            'role': 'viewer',
            'department': 'Marketing',
        },
    ]

    created_users = []
    created_members = []

    for user_data in users_data:
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            name=user_data['name'],
            email=user_data['email'],
            role=user_data['role'],
            department=user_data['department'],
            department_id=user_data.get('department_id'),
            status='active',
            is_active=True
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()

        # Create user settings
        settings = UserSettings(
            id=str(uuid.uuid4()),
            user_id=user.id,
            theme='system',
            language='pt-BR'
        )
        db.session.add(settings)

        # Create team member
        team_member = TeamMember(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name=user_data['name'],
            email=user_data['email'],
            role=user_data['role'].title(),
            department=user_data['department'],
            status='active'
        )
        db.session.add(team_member)

        created_users.append(user)
        created_members.append(team_member)

    db.session.commit()
    print(f"[OK] Created {len(created_users)} test users")
    print(f"[OK] Created {len(created_members)} team members")

    return created_users, created_members


def create_sample_projects(users, members):
    """Create sample projects"""
    admin = users[0]

    projects_data = [
        {
            'name': 'Website Institucional',
            'description': 'Desenvolvimento do novo website da empresa',
            'color': '#3B82F6',
            'status': 'active',
            'progress': 65,
            'days_offset': (-15, 30),
        },
        {
            'name': 'App Mobile',
            'description': 'Aplicativo mobile para clientes',
            'color': '#10B981',
            'status': 'planning',
            'progress': 10,
            'days_offset': (5, 60),
        },
        {
            'name': 'Sistema de Relatórios',
            'description': 'Dashboard de relatórios gerenciais',
            'color': '#F59E0B',
            'status': 'active',
            'progress': 40,
            'days_offset': (-10, 20),
        },
    ]

    created_projects = []

    for proj_data in projects_data:
        start_offset, end_offset = proj_data['days_offset']

        project = Project(
            id=str(uuid.uuid4()),
            name=proj_data['name'],
            description=proj_data['description'],
            color=proj_data['color'],
            status=proj_data['status'],
            progress=proj_data['progress'],
            start_date=datetime.now().date() + timedelta(days=start_offset),
            end_date=datetime.now().date() + timedelta(days=end_offset),
            owner_id=admin.id
        )

        # Add team members to project
        for member in members[:3]:
            project.team_members.append(member)

        db.session.add(project)
        created_projects.append(project)

    db.session.commit()
    print(f"[OK] Created {len(created_projects)} projects")

    return created_projects


def create_sample_tasks(projects, members):
    """Create sample tasks"""

    tasks_data = [
        # Website tasks
        {'name': 'Design da Homepage', 'status': 'completed', 'progress': 100, 'priority': 'high'},
        {'name': 'Desenvolvimento Frontend', 'status': 'in-progress', 'progress': 60, 'priority': 'high'},
        {'name': 'Integração com API', 'status': 'todo', 'progress': 0, 'priority': 'medium'},
        {'name': 'Testes de Usabilidade', 'status': 'todo', 'progress': 0, 'priority': 'low'},
        # App tasks
        {'name': 'Prototipação', 'status': 'in-progress', 'progress': 30, 'priority': 'high'},
        {'name': 'Setup React Native', 'status': 'completed', 'progress': 100, 'priority': 'high'},
        # Reports tasks
        {'name': 'Modelagem de Dados', 'status': 'completed', 'progress': 100, 'priority': 'high'},
        {'name': 'Criação de Gráficos', 'status': 'in-progress', 'progress': 50, 'priority': 'medium'},
    ]

    created_tasks = []
    task_idx = 0

    for i, project in enumerate(projects):
        # Assign 2-3 tasks per project
        num_tasks = 4 if i == 0 else 2

        for j in range(num_tasks):
            if task_idx >= len(tasks_data):
                break

            task_data = tasks_data[task_idx]

            task = Task(
                id=str(uuid.uuid4()),
                name=task_data['name'],
                description=f"Descrição da tarefa: {task_data['name']}",
                start_date=project.start_date + timedelta(days=j * 5),
                end_date=project.start_date + timedelta(days=(j + 1) * 5 + 3),
                status=task_data['status'],
                priority=task_data['priority'],
                progress=task_data['progress'],
                project_id=project.id,
                assignee_id=members[j % len(members)].id
            )
            db.session.add(task)
            created_tasks.append(task)
            task_idx += 1

    db.session.commit()
    print(f"[OK] Created {len(created_tasks)} tasks")

    return created_tasks


def run_seed():
    """Run the complete seed process"""
    app = create_app()

    with app.app_context():
        print("\n" + "="*50)
        print("ProjectFlow - Database Seed")
        print("="*50 + "\n")

        # Check if database already has data
        existing_users = User.query.first()
        if existing_users:
            print("[!] Database already has data.")
            confirm = input("Do you want to clear and reseed? (y/N): ")
            if confirm.lower() != 'y':
                print("Seed cancelled.")
                return

            # Clear existing data
            print("\nClearing existing data...")
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
            db.session.execute(db.text("TRUNCATE TABLE share_links"))
            db.session.execute(db.text("TRUNCATE TABLE tasks"))
            db.session.execute(db.text("TRUNCATE TABLE project_members"))
            db.session.execute(db.text("TRUNCATE TABLE projects"))
            db.session.execute(db.text("TRUNCATE TABLE team_members"))
            db.session.execute(db.text("TRUNCATE TABLE user_settings"))
            db.session.execute(db.text("TRUNCATE TABLE users"))
            db.session.execute(db.text("TRUNCATE TABLE roles"))
            db.session.execute(db.text("TRUNCATE TABLE departments"))
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            db.session.commit()
            print("[OK] Data cleared\n")

        # Create seed data
        departments = create_departments()
        roles = create_roles()
        users, members = create_test_users(departments)
        projects = create_sample_projects(users, members)
        tasks = create_sample_tasks(projects, members)

        print("\n" + "="*50)
        print("Seed completed successfully!")
        print("="*50)
        print("\nTest Accounts:")
        print("-" * 40)
        print("Admin:   admin@projectflow.com   / admin123")
        print("Gerente: gerente@projectflow.com / gerente123")
        print("Membro:  membro@projectflow.com  / membro123")
        print("Viewer:  viewer@projectflow.com  / viewer123")
        print("-" * 40 + "\n")


if __name__ == '__main__':
    run_seed()
