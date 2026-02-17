"""
Model para gerenciamento de tarefas.
"""
from datetime import datetime, date
from db import Database


class TaskModel:
    """Operações CRUD para tarefas."""

    VALID_STATUSES = ('todo', 'doing', 'review', 'done')

    @staticmethod
    def _validate_dates(start_date, end_date):
        """
        Valida se as datas são válidas e se início é antes do fim.

        Args:
            start_date: Data de início (string YYYY-MM-DD ou date).
            end_date: Data de fim (string YYYY-MM-DD ou date).

        Returns:
            Tupla (start_date, end_date) como objetos date.

        Raises:
            ValueError: Se as datas forem inválidas.
        """
        # Converte strings para date
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Data de início inválida. Use o formato YYYY-MM-DD")

        if isinstance(end_date, str):
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Data de fim inválida. Use o formato YYYY-MM-DD")

        # Valida ordem das datas
        if start_date > end_date:
            raise ValueError("A data de início deve ser anterior ou igual à data de fim")

        return start_date, end_date

    @staticmethod
    def _validate_status(status):
        """
        Valida se o status é permitido.

        Args:
            status: Status da tarefa.

        Raises:
            ValueError: Se o status não for válido.
        """
        if status not in TaskModel.VALID_STATUSES:
            raise ValueError(
                f"Status inválido. Valores permitidos: {', '.join(TaskModel.VALID_STATUSES)}"
            )

    @staticmethod
    def _calculate_duration(start_date, end_date):
        """
        Calcula a duração em dias entre duas datas.

        Args:
            start_date: Data de início.
            end_date: Data de fim.

        Returns:
            Número de dias (incluindo início e fim).
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        return (end_date - start_date).days + 1

    @staticmethod
    def _format_task(row):
        """
        Formata uma linha do banco para dicionário de tarefa.

        Args:
            row: Dicionário com dados do banco.

        Returns:
            Dicionário formatado da tarefa.
        """
        return {
            'id': row['id'],
            'project_id': row['project_id'],
            'name': row['name'],
            'start_date': row['start_date'].isoformat() if row['start_date'] else None,
            'end_date': row['end_date'].isoformat() if row['end_date'] else None,
            'duration_days': TaskModel._calculate_duration(
                row['start_date'], row['end_date']
            ) if row['start_date'] and row['end_date'] else 0,
            'status': row['status'],
            'assignee': row['assignee'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
        }

    @staticmethod
    def get_by_project(project_id):
        """
        Retorna todas as tarefas de um projeto.

        Args:
            project_id: ID do projeto.

        Returns:
            Lista de tarefas ordenadas por data de início.
        """
        query = """
            SELECT id, project_id, name, start_date, end_date,
                   status, assignee, created_at, updated_at
            FROM tasks
            WHERE project_id = %s
            ORDER BY start_date ASC, id ASC
        """
        results = Database.execute_query(query, (project_id,))
        return [TaskModel._format_task(row) for row in results]

    @staticmethod
    def get_by_id(task_id):
        """
        Retorna uma tarefa pelo ID.

        Args:
            task_id: ID da tarefa.

        Returns:
            Dicionário com dados da tarefa ou None.
        """
        query = """
            SELECT id, project_id, name, start_date, end_date,
                   status, assignee, created_at, updated_at
            FROM tasks
            WHERE id = %s
        """
        result = Database.execute_query(query, (task_id,), fetch_one=True)

        if result:
            return TaskModel._format_task(result)
        return None

    @staticmethod
    def create(project_id, name, start_date, end_date, status='todo', assignee=None):
        """
        Cria uma nova tarefa.

        Args:
            project_id: ID do projeto (obrigatório).
            name: Nome da tarefa (obrigatório).
            start_date: Data de início (obrigatório).
            end_date: Data de fim (obrigatório).
            status: Status da tarefa (default: 'todo').
            assignee: Responsável pela tarefa (opcional).

        Returns:
            Dicionário com dados da tarefa criada.

        Raises:
            ValueError: Se os dados forem inválidos.
        """
        # Validações
        if not name or not name.strip():
            raise ValueError("O nome da tarefa é obrigatório")

        start_date, end_date = TaskModel._validate_dates(start_date, end_date)
        TaskModel._validate_status(status)

        name = name.strip()
        assignee = assignee.strip() if assignee else None

        query = """
            INSERT INTO tasks (project_id, name, start_date, end_date, status, assignee)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        task_id = Database.execute_insert(
            query,
            (project_id, name, start_date, end_date, status, assignee)
        )

        return TaskModel.get_by_id(task_id)

    @staticmethod
    def update(task_id, **kwargs):
        """
        Atualiza uma tarefa existente.

        Args:
            task_id: ID da tarefa.
            **kwargs: Campos a atualizar (name, start_date, end_date, status, assignee).

        Returns:
            Dicionário com dados da tarefa atualizada ou None.

        Raises:
            ValueError: Se os dados forem inválidos.
        """
        # Verifica se a tarefa existe
        task = TaskModel.get_by_id(task_id)
        if not task:
            return None

        updates = []
        params = []

        # Processa cada campo
        if 'name' in kwargs:
            name = kwargs['name']
            if not name or not name.strip():
                raise ValueError("O nome da tarefa não pode estar vazio")
            updates.append("name = %s")
            params.append(name.strip())

        if 'start_date' in kwargs or 'end_date' in kwargs:
            start = kwargs.get('start_date', task['start_date'])
            end = kwargs.get('end_date', task['end_date'])
            start, end = TaskModel._validate_dates(start, end)

            if 'start_date' in kwargs:
                updates.append("start_date = %s")
                params.append(start)
            if 'end_date' in kwargs:
                updates.append("end_date = %s")
                params.append(end)

        if 'status' in kwargs:
            status = kwargs['status']
            TaskModel._validate_status(status)
            updates.append("status = %s")
            params.append(status)

        if 'assignee' in kwargs:
            assignee = kwargs['assignee']
            updates.append("assignee = %s")
            params.append(assignee.strip() if assignee else None)

        if not updates:
            return task

        params.append(task_id)
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s"
        Database.execute_update(query, tuple(params))

        return TaskModel.get_by_id(task_id)

    @staticmethod
    def delete(task_id):
        """
        Deleta uma tarefa.

        Args:
            task_id: ID da tarefa.

        Returns:
            True se deletada, False se não encontrada.
        """
        query = "DELETE FROM tasks WHERE id = %s"
        rows_affected = Database.execute_update(query, (task_id,))
        return rows_affected > 0

    @staticmethod
    def get_dashboard_metrics():
        """
        Retorna métricas para o dashboard.

        Returns:
            Dicionário com métricas agregadas.
        """
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo,
                SUM(CASE WHEN status = 'doing' THEN 1 ELSE 0 END) as doing,
                SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as review,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
            FROM tasks
        """
        result = Database.execute_query(query, fetch_one=True)

        # Métricas por projeto
        projects_query = """
            SELECT COUNT(*) as total_projects
            FROM projects
        """
        projects_result = Database.execute_query(projects_query, fetch_one=True)

        # Tarefas atrasadas (end_date < hoje e status != done)
        overdue_query = """
            SELECT COUNT(*) as overdue
            FROM tasks
            WHERE end_date < CURDATE() AND status != 'done'
        """
        overdue_result = Database.execute_query(overdue_query, fetch_one=True)

        return {
            'total_tasks': result['total'] or 0,
            'todo': int(result['todo'] or 0),
            'doing': int(result['doing'] or 0),
            'review': int(result['review'] or 0),
            'done': int(result['done'] or 0),
            'total_projects': projects_result['total_projects'] or 0,
            'overdue': overdue_result['overdue'] or 0,
            'completion_rate': round(
                (int(result['done'] or 0) / result['total'] * 100), 1
            ) if result['total'] else 0
        }

    @staticmethod
    def get_all():
        """
        Retorna todas as tarefas.

        Returns:
            Lista de todas as tarefas.
        """
        query = """
            SELECT t.id, t.project_id, t.name, t.start_date, t.end_date,
                   t.status, t.assignee, t.created_at, t.updated_at,
                   p.name as project_name
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            ORDER BY t.start_date ASC, t.id ASC
        """
        results = Database.execute_query(query)

        tasks = []
        for row in results:
            task = TaskModel._format_task(row)
            task['project_name'] = row['project_name']
            tasks.append(task)

        return tasks
