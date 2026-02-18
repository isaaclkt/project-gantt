"""
Seed database with test data
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
from app import create_app
from app.config.database import db
from app.models.user import User, UserSettings
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.task import Task
from app.models.department import Department, Role

app = create_app()

def seed_database():
    with app.app_context():
        print("Seeding database...")

        # Clear existing data (in reverse order of dependencies)
        print("Clearing existing data...")
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
        db.session.execute(db.text("DELETE FROM tasks"))
        db.session.execute(db.text("DELETE FROM project_members"))
        db.session.execute(db.text("DELETE FROM projects"))
        db.session.execute(db.text("DELETE FROM team_members"))
        db.session.execute(db.text("DELETE FROM user_settings"))
        db.session.execute(db.text("DELETE FROM users"))
        db.session.execute(db.text("DELETE FROM departments"))
        db.session.execute(db.text("DELETE FROM roles"))
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
        db.session.commit()

        # Create departments
        print("Creating departments...")
        departments = [
            Department(id='dept1', name='Gestão', description='Gerenciamento de projetos e equipes'),
            Department(id='dept2', name='Desenvolvimento', description='Desenvolvimento de software'),
            Department(id='dept3', name='Design', description='Design de interfaces e experiência'),
            Department(id='dept4', name='Qualidade', description='Garantia de qualidade e testes'),
            Department(id='dept5', name='Infraestrutura', description='DevOps e infraestrutura'),
        ]
        for dept in departments:
            db.session.add(dept)
        db.session.commit()

        # Create roles
        print("Creating roles...")
        roles = [
            Role(id='role1', name='Project Manager', description='Gerente de projetos'),
            Role(id='role2', name='Frontend Developer', description='Desenvolvedor frontend'),
            Role(id='role3', name='Backend Developer', description='Desenvolvedor backend'),
            Role(id='role4', name='UI/UX Designer', description='Designer de interface'),
            Role(id='role5', name='QA Engineer', description='Engenheiro de qualidade'),
            Role(id='role6', name='DevOps Engineer', description='Engenheiro DevOps'),
        ]
        for role in roles:
            db.session.add(role)
        db.session.commit()

        # Create users with proper password hashes
        print("Creating users...")
        users_data = [
            ('u1', 'Admin User', 'admin@teste.com', 'admin', 'dept1'),
            ('u2', 'Manager User', 'manager@teste.com', 'manager', 'dept1'),
            ('u3', 'Member User', 'member@teste.com', 'member', 'dept2'),
            ('u4', 'Viewer User', 'viewer@teste.com', 'viewer', 'dept2'),
        ]

        users = []
        for uid, name, email, role, dept_id in users_data:
            user = User(
                id=uid,
                name=name,
                email=email,
                role=role,
                department_id=dept_id,
                department=dept_id.replace('dept', 'Departamento '),
                timezone='America/Sao_Paulo',
                status='active'
            )
            user.set_password('123456')  # Default password for all test users
            users.append(user)
            db.session.add(user)
        db.session.commit()

        # Create user settings
        print("Creating user settings...")
        themes = ['dark', 'system', 'light', 'system']
        for i, user in enumerate(users):
            settings = UserSettings(
                user_id=user.id,
                theme=themes[i],
                language='pt-BR'
            )
            db.session.add(settings)
        db.session.commit()

        # Create team members
        print("Creating team members...")
        team_members_data = [
            ('tm1', 'u1', 'role1', 'dept1', 'Administrador', 'active'),
            ('tm2', 'u2', 'role1', 'dept1', 'Gerente de Projetos', 'active'),
            ('tm3', 'u3', 'role2', 'dept2', 'Desenvolvedor', 'active'),
            ('tm4', 'u4', 'role2', 'dept2', 'Visualizador', 'active'),
        ]

        team_members = []
        for tm_id, user_id, role_id, dept_id, job_title, status in team_members_data:
            user = User.query.get(user_id)
            tm = TeamMember(
                id=tm_id,
                user_id=user_id,
                role_id=role_id,
                department_id=dept_id,
                name=user.name,
                email=user.email,
                avatar=user.avatar,
                role=job_title,
                department=user.department,
                job_title=job_title,
                status=status
            )
            team_members.append(tm)
            db.session.add(tm)
        db.session.commit()

        # Create projects
        print("Creating projects...")
        today = datetime.now().date()
        projects_data = [
            ('p1', 'Website Redesign', 'Redesign completo do website corporativo', '#3B82F6', 'active', 65, today - timedelta(days=10), today + timedelta(days=20), 'u1'),
            ('p2', 'Mobile App', 'Desenvolvimento do aplicativo mobile', '#10B981', 'active', 35, today - timedelta(days=5), today + timedelta(days=30), 'u2'),
            ('p3', 'API Integration', 'Integração com APIs de terceiros', '#F59E0B', 'planning', 10, today + timedelta(days=5), today + timedelta(days=25), 'u2'),
        ]

        projects = []
        for pid, name, desc, color, status, progress, start, end, owner_id in projects_data:
            project = Project(
                id=pid,
                name=name,
                description=desc,
                color=color,
                status=status,
                progress=progress,
                start_date=start,
                end_date=end,
                owner_id=owner_id
            )
            projects.append(project)
            db.session.add(project)
        db.session.commit()

        # Add project members
        print("Adding project members...")
        project_members_data = [
            ('p1', 'tm1'), ('p1', 'tm2'), ('p1', 'tm3'), ('p1', 'tm4'),
            ('p2', 'tm2'), ('p2', 'tm3'),
            ('p3', 'tm2'), ('p3', 'tm3'),
        ]

        for project_id, tm_id in project_members_data:
            project = Project.query.get(project_id)
            tm = TeamMember.query.get(tm_id)
            if project and tm:
                project.team_members.append(tm)
        db.session.commit()

        # Create tasks
        print("Creating tasks...")
        tasks_data = [
            ('t1', 'Design da Homepage', 'Criar novo design da página inicial', today - timedelta(days=10), today - timedelta(days=3), 'completed', 'high', 100, 'tm3', 'p1'),
            ('t2', 'Implementação Frontend', 'Desenvolver componentes React', today - timedelta(days=5), today + timedelta(days=5), 'in-progress', 'high', 60, 'tm3', 'p1'),
            ('t3', 'Revisão de Código', 'Code review do frontend', today + timedelta(days=3), today + timedelta(days=7), 'todo', 'medium', 0, 'tm2', 'p1'),
            ('t4', 'Setup do Projeto Mobile', 'Configurar ambiente React Native', today - timedelta(days=5), today - timedelta(days=2), 'completed', 'high', 100, 'tm3', 'p2'),
            ('t5', 'Desenvolvimento de Telas', 'Criar telas principais do app', today - timedelta(days=2), today + timedelta(days=10), 'in-progress', 'high', 30, 'tm3', 'p2'),
            ('t6', 'API Backend Mobile', 'Desenvolver endpoints para o app', today + timedelta(days=1), today + timedelta(days=15), 'review', 'high', 80, 'tm3', 'p2'),
            ('t7', 'Análise de Requisitos', 'Levantar requisitos de integração', today + timedelta(days=5), today + timedelta(days=10), 'todo', 'medium', 0, 'tm3', 'p3'),
        ]

        for tid, name, desc, start, end, status, priority, progress, assignee_id, project_id in tasks_data:
            task = Task(
                id=tid,
                name=name,
                description=desc,
                start_date=start,
                end_date=end,
                status=status,
                priority=priority,
                progress=progress,
                assignee_id=assignee_id,
                project_id=project_id
            )
            db.session.add(task)
        db.session.commit()

        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nTest users created:")
        print("-" * 40)
        for uid, name, email, role, _ in users_data:
            print(f"  {name}")
            print(f"    Email: {email}")
            print(f"    Password: 123456")
            print(f"    Role: {role}")
            print()
        print("="*50)

if __name__ == '__main__':
    seed_database()
