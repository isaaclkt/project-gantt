"""
Model para gerenciamento de projetos.
"""
from datetime import datetime
from db import Database


class ProjectModel:
    """Operações CRUD para projetos."""

    @staticmethod
    def get_all():
        """
        Retorna todos os projetos ordenados por data de criação.

        Returns:
            Lista de projetos com contagem de tarefas.
        """
        query = """
            SELECT
                p.id,
                p.name,
                p.description,
                p.created_at,
                p.updated_at,
                COUNT(t.id) as task_count,
                SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed_tasks
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """
        results = Database.execute_query(query)

        projects = []
        for row in results:
            project = {
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                'task_count': row['task_count'] or 0,
                'completed_tasks': int(row['completed_tasks'] or 0),
                'progress': 0
            }
            # Calcula progresso
            if project['task_count'] > 0:
                project['progress'] = round(
                    (project['completed_tasks'] / project['task_count']) * 100, 1
                )
            projects.append(project)

        return projects

    @staticmethod
    def get_by_id(project_id):
        """
        Retorna um projeto pelo ID.

        Args:
            project_id: ID do projeto.

        Returns:
            Dicionário com dados do projeto ou None.
        """
        query = """
            SELECT
                p.id,
                p.name,
                p.description,
                p.created_at,
                p.updated_at,
                COUNT(t.id) as task_count
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.id = %s
            GROUP BY p.id
        """
        result = Database.execute_query(query, (project_id,), fetch_one=True)

        if result:
            return {
                'id': result['id'],
                'name': result['name'],
                'description': result['description'],
                'created_at': result['created_at'].isoformat() if result['created_at'] else None,
                'updated_at': result['updated_at'].isoformat() if result['updated_at'] else None,
                'task_count': result['task_count'] or 0
            }
        return None

    @staticmethod
    def create(name, description=None):
        """
        Cria um novo projeto.

        Args:
            name: Nome do projeto (obrigatório).
            description: Descrição do projeto (opcional).

        Returns:
            Dicionário com dados do projeto criado.

        Raises:
            ValueError: Se o nome estiver vazio.
        """
        if not name or not name.strip():
            raise ValueError("O nome do projeto é obrigatório")

        name = name.strip()
        description = description.strip() if description else None

        query = """
            INSERT INTO projects (name, description)
            VALUES (%s, %s)
        """
        project_id = Database.execute_insert(query, (name, description))

        return ProjectModel.get_by_id(project_id)

    @staticmethod
    def update(project_id, name=None, description=None):
        """
        Atualiza um projeto existente.

        Args:
            project_id: ID do projeto.
            name: Novo nome (opcional).
            description: Nova descrição (opcional).

        Returns:
            Dicionário com dados do projeto atualizado ou None.
        """
        # Verifica se o projeto existe
        project = ProjectModel.get_by_id(project_id)
        if not project:
            return None

        updates = []
        params = []

        if name is not None:
            if not name.strip():
                raise ValueError("O nome do projeto não pode estar vazio")
            updates.append("name = %s")
            params.append(name.strip())

        if description is not None:
            updates.append("description = %s")
            params.append(description.strip() if description else None)

        if not updates:
            return project

        params.append(project_id)
        query = f"UPDATE projects SET {', '.join(updates)} WHERE id = %s"
        Database.execute_update(query, tuple(params))

        return ProjectModel.get_by_id(project_id)

    @staticmethod
    def delete(project_id):
        """
        Deleta um projeto e suas tarefas (CASCADE).

        Args:
            project_id: ID do projeto.

        Returns:
            True se deletado, False se não encontrado.
        """
        query = "DELETE FROM projects WHERE id = %s"
        rows_affected = Database.execute_update(query, (project_id,))
        return rows_affected > 0

    @staticmethod
    def exists(project_id):
        """
        Verifica se um projeto existe.

        Args:
            project_id: ID do projeto.

        Returns:
            True se existe, False caso contrário.
        """
        query = "SELECT 1 FROM projects WHERE id = %s"
        result = Database.execute_query(query, (project_id,), fetch_one=True)
        return result is not None
