"""
Rotas da API REST para o sistema de gerenciamento de projetos.

Endpoints:
    GET  /api/projects          - Lista todos os projetos
    POST /api/projects          - Cria um novo projeto
    GET  /api/projects/<id>     - Obtém um projeto específico
    PUT  /api/projects/<id>     - Atualiza um projeto
    DELETE /api/projects/<id>   - Deleta um projeto
    GET  /api/projects/<id>/tasks - Lista tarefas do projeto
    GET  /api/tasks             - Lista todas as tarefas
    POST /api/tasks             - Cria uma nova tarefa
    GET  /api/tasks/<id>        - Obtém uma tarefa específica
    PUT  /api/tasks/<id>        - Atualiza uma tarefa
    DELETE /api/tasks/<id>      - Deleta uma tarefa
    GET  /api/dashboard         - Métricas do dashboard
"""
from flask import Blueprint, request, jsonify
from models import ProjectModel, TaskModel
from mysql.connector import Error as MySQLError

api_bp = Blueprint('api', __name__, url_prefix='/api')


def error_response(message, status_code=400):
    """Retorna uma resposta de erro padronizada."""
    return jsonify({
        'success': False,
        'error': message
    }), status_code


def success_response(data=None, message=None, status_code=200):
    """Retorna uma resposta de sucesso padronizada."""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status_code


# ==================== PROJECTS ====================

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    Lista todos os projetos.

    Returns:
        JSON com lista de projetos e contagem de tarefas.
    """
    try:
        projects = ProjectModel.get_all()
        return success_response(projects)
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/projects', methods=['POST'])
def create_project():
    """
    Cria um novo projeto.

    Body JSON:
        - name (string, obrigatório): Nome do projeto
        - description (string, opcional): Descrição do projeto

    Returns:
        JSON com dados do projeto criado (201) ou erro.
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("Dados JSON inválidos ou ausentes")

        name = data.get('name')
        description = data.get('description')

        if not name:
            return error_response("O campo 'name' é obrigatório")

        project = ProjectModel.create(name, description)
        return success_response(project, "Projeto criado com sucesso", 201)

    except ValueError as e:
        return error_response(str(e))
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    Obtém um projeto específico pelo ID.

    Args:
        project_id: ID do projeto.

    Returns:
        JSON com dados do projeto ou 404.
    """
    try:
        project = ProjectModel.get_by_id(project_id)

        if not project:
            return error_response("Projeto não encontrado", 404)

        return success_response(project)

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    Atualiza um projeto existente.

    Args:
        project_id: ID do projeto.

    Body JSON:
        - name (string, opcional): Novo nome
        - description (string, opcional): Nova descrição

    Returns:
        JSON com dados do projeto atualizado ou erro.
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("Dados JSON inválidos ou ausentes")

        project = ProjectModel.update(
            project_id,
            name=data.get('name'),
            description=data.get('description')
        )

        if not project:
            return error_response("Projeto não encontrado", 404)

        return success_response(project, "Projeto atualizado com sucesso")

    except ValueError as e:
        return error_response(str(e))
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    Deleta um projeto e suas tarefas.

    Args:
        project_id: ID do projeto.

    Returns:
        JSON de confirmação ou 404.
    """
    try:
        deleted = ProjectModel.delete(project_id)

        if not deleted:
            return error_response("Projeto não encontrado", 404)

        return success_response(message="Projeto deletado com sucesso")

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/projects/<int:project_id>/tasks', methods=['GET'])
def get_project_tasks(project_id):
    """
    Lista todas as tarefas de um projeto.

    Args:
        project_id: ID do projeto.

    Returns:
        JSON com lista de tarefas ou 404 se projeto não existe.
    """
    try:
        # Verifica se o projeto existe
        if not ProjectModel.exists(project_id):
            return error_response("Projeto não encontrado", 404)

        tasks = TaskModel.get_by_project(project_id)
        return success_response(tasks)

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


# ==================== TASKS ====================

@api_bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    """
    Lista todas as tarefas de todos os projetos.

    Returns:
        JSON com lista de todas as tarefas.
    """
    try:
        tasks = TaskModel.get_all()
        return success_response(tasks)
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """
    Cria uma nova tarefa.

    Body JSON:
        - project_id (int, obrigatório): ID do projeto
        - name (string, obrigatório): Nome da tarefa
        - start_date (string, obrigatório): Data início (YYYY-MM-DD)
        - end_date (string, obrigatório): Data fim (YYYY-MM-DD)
        - status (string, opcional): Status (todo, doing, review, done)
        - assignee (string, opcional): Responsável

    Returns:
        JSON com dados da tarefa criada (201) ou erro.
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("Dados JSON inválidos ou ausentes")

        # Validações de campos obrigatórios
        required_fields = ['project_id', 'name', 'start_date', 'end_date']
        missing = [f for f in required_fields if not data.get(f)]

        if missing:
            return error_response(f"Campos obrigatórios ausentes: {', '.join(missing)}")

        # Verifica se o projeto existe
        if not ProjectModel.exists(data['project_id']):
            return error_response("Projeto não encontrado", 404)

        task = TaskModel.create(
            project_id=data['project_id'],
            name=data['name'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            status=data.get('status', 'todo'),
            assignee=data.get('assignee')
        )

        return success_response(task, "Tarefa criada com sucesso", 201)

    except ValueError as e:
        return error_response(str(e))
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Obtém uma tarefa específica pelo ID.

    Args:
        task_id: ID da tarefa.

    Returns:
        JSON com dados da tarefa ou 404.
    """
    try:
        task = TaskModel.get_by_id(task_id)

        if not task:
            return error_response("Tarefa não encontrada", 404)

        return success_response(task)

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Atualiza uma tarefa existente.

    Args:
        task_id: ID da tarefa.

    Body JSON (todos opcionais):
        - name (string): Novo nome
        - start_date (string): Nova data início (YYYY-MM-DD)
        - end_date (string): Nova data fim (YYYY-MM-DD)
        - status (string): Novo status
        - assignee (string): Novo responsável

    Returns:
        JSON com dados da tarefa atualizada ou erro.
    """
    try:
        data = request.get_json()

        if not data:
            return error_response("Dados JSON inválidos ou ausentes")

        # Filtra apenas campos permitidos
        allowed_fields = ['name', 'start_date', 'end_date', 'status', 'assignee']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return error_response("Nenhum campo válido para atualização")

        task = TaskModel.update(task_id, **update_data)

        if not task:
            return error_response("Tarefa não encontrada", 404)

        return success_response(task, "Tarefa atualizada com sucesso")

    except ValueError as e:
        return error_response(str(e))
    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Deleta uma tarefa.

    Args:
        task_id: ID da tarefa.

    Returns:
        JSON de confirmação ou 404.
    """
    try:
        deleted = TaskModel.delete(task_id)

        if not deleted:
            return error_response("Tarefa não encontrada", 404)

        return success_response(message="Tarefa deletada com sucesso")

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


# ==================== DASHBOARD ====================

@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Retorna métricas do dashboard.

    Returns:
        JSON com:
        - total_tasks: Total de tarefas
        - todo: Tarefas a fazer
        - doing: Tarefas em andamento
        - review: Tarefas em revisão
        - done: Tarefas concluídas
        - total_projects: Total de projetos
        - overdue: Tarefas atrasadas
        - completion_rate: Taxa de conclusão (%)
    """
    try:
        metrics = TaskModel.get_dashboard_metrics()
        return success_response(metrics)

    except MySQLError as e:
        return error_response(f"Erro no banco de dados: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Erro interno: {str(e)}", 500)


# ==================== ERROR HANDLERS ====================

@api_bp.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas."""
    return error_response("Endpoint não encontrado", 404)


@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handler para métodos não permitidos."""
    return error_response("Método não permitido", 405)


@api_bp.errorhandler(500)
def internal_error(error):
    """Handler para erros internos."""
    return error_response("Erro interno do servidor", 500)
