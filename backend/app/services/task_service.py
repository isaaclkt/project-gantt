"""
Task Service - Business logic for tasks
"""
from datetime import datetime
from typing import Optional, List
from app.config.database import db
from app.models import Task, Project
from app.utils.sanitizer import sanitize_dict, TASK_SCHEMA


class TaskService:
    """Service class for task operations"""

    @staticmethod
    def _sanitize_task_data(data: dict) -> dict:
        """Sanitize task input data before processing."""
        return sanitize_dict(data, TASK_SCHEMA)

    @staticmethod
    def get_all(
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[List[Task], int]:
        """
        Get all tasks with optional filtering and pagination
        Returns: (tasks, total_count)
        """
        query = Task.query

        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if priority:
            query = query.filter(Task.priority == priority)

        # Order by start_date
        query = query.order_by(Task.start_date.asc())

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        tasks = query.offset((page - 1) * limit).limit(limit).all()

        return tasks, total

    @staticmethod
    def get_by_id(task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return Task.query.get(task_id)

    @staticmethod
    def get_by_project(project_id: str) -> List[Task]:
        """Get all tasks for a specific project"""
        return Task.query.filter(Task.project_id == project_id).order_by(Task.start_date.asc()).all()

    @staticmethod
    def create(data: dict) -> Task:
        """
        Create a new task with sanitized input
        """
        # Sanitize input data
        sanitized = TaskService._sanitize_task_data(data)

        # Parse dates
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

        task = Task(
            name=sanitized.get('name', data['name']),
            description=sanitized.get('description', ''),
            start_date=start_date,
            end_date=end_date,
            status=sanitized.get('status', 'todo'),
            priority=sanitized.get('priority', 'medium'),
            progress=sanitized.get('progress', 0),
            assignee_id=data.get('assigneeId'),
            project_id=data['projectId']
        )

        db.session.add(task)
        db.session.commit()

        # Update project progress
        TaskService._update_project_progress(task.project_id)

        return task

    @staticmethod
    def update(task_id: str, data: dict) -> Optional[Task]:
        """
        Update an existing task with sanitized input
        """
        task = Task.query.get(task_id)
        if not task:
            return None

        # Sanitize input data
        sanitized = TaskService._sanitize_task_data(data)

        # Update fields if provided (use sanitized values)
        if 'name' in sanitized:
            task.name = sanitized['name']
        if 'description' in sanitized:
            task.description = sanitized['description']
        if 'status' in sanitized:
            task.status = sanitized['status']
            # Auto-update progress based on status
            if sanitized['status'] == 'completed':
                task.progress = 100
            elif sanitized['status'] == 'todo' and task.progress == 100:
                task.progress = 0
        if 'priority' in sanitized:
            task.priority = sanitized['priority']
        if 'progress' in sanitized:
            task.progress = sanitized['progress']
        if 'startDate' in data:
            task.start_date = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        if 'endDate' in data:
            task.end_date = datetime.strptime(data['endDate'], '%Y-%m-%d').date()
        if 'assigneeId' in data:
            task.assignee_id = data['assigneeId'] if data['assigneeId'] else None
        if 'projectId' in data:
            task.project_id = data['projectId']

        db.session.commit()

        # Update project progress
        TaskService._update_project_progress(task.project_id)

        return task

    @staticmethod
    def delete(task_id: str) -> bool:
        """
        Delete a task
        """
        task = Task.query.get(task_id)
        if not task:
            return False

        project_id = task.project_id

        db.session.delete(task)
        db.session.commit()

        # Update project progress
        TaskService._update_project_progress(project_id)

        return True

    @staticmethod
    def update_status(task_id: str, status: str) -> Optional[Task]:
        """Quick update just the status of a task with validation"""
        task = Task.query.get(task_id)
        if not task:
            return None

        # Validate status value
        valid_statuses = ['todo', 'in-progress', 'review', 'completed']
        if status not in valid_statuses:
            return None

        task.status = status

        # Auto-update progress based on status
        if status == 'completed':
            task.progress = 100
        elif status == 'todo':
            task.progress = 0

        db.session.commit()

        # Update project progress
        TaskService._update_project_progress(task.project_id)

        return task

    @staticmethod
    def update_progress(task_id: str, progress: int) -> Optional[Task]:
        """Quick update just the progress of a task"""
        task = Task.query.get(task_id)
        if not task:
            return None

        task.progress = max(0, min(100, progress))

        # Auto-update status based on progress
        if progress == 100:
            task.status = 'completed'
        elif progress == 0 and task.status == 'completed':
            task.status = 'todo'

        db.session.commit()

        # Update project progress
        TaskService._update_project_progress(task.project_id)

        return task

    @staticmethod
    def _update_project_progress(project_id: str):
        """Internal method to update project progress"""
        project = Project.query.get(project_id)
        if project:
            project.update_progress()
            db.session.commit()
