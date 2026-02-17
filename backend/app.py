"""
Aplicação principal Flask para o sistema de gerenciamento de projetos.

ProjectFlow Gantt - Sistema de Gerenciamento de Projetos com visualização Gantt

Endpoints disponíveis:
    /api/projects          - Gerenciamento de projetos
    /api/tasks             - Gerenciamento de tarefas
    /api/dashboard         - Métricas do dashboard

Uso:
    python app.py          - Inicia o servidor de desenvolvimento
    flask run              - Inicia via Flask CLI

Variáveis de ambiente:
    FLASK_ENV              - development, production, testing
    DB_HOST                - Host do MySQL
    DB_PORT                - Porta do MySQL
    DB_USER                - Usuário do MySQL
    DB_PASSWORD            - Senha do MySQL
    DB_NAME                - Nome do banco de dados
"""
import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from db import Database, init_database
from routes import api_bp


def create_app(config_name=None):
    """
    Factory function para criar a aplicação Flask.

    Args:
        config_name: Nome da configuração (development, production, testing).

    Returns:
        Instância configurada do Flask.
    """
    app = Flask(__name__)

    # Carrega configurações
    config = get_config()
    app.config.from_object(config)

    # Habilita CORS para todas as rotas /api
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Registra blueprints
    app.register_blueprint(api_bp)

    # Rota de health check
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar se a API está funcionando."""
        return jsonify({
            'status': 'healthy',
            'message': 'ProjectFlow Gantt API está funcionando'
        })

    # Rota raiz
    @app.route('/', methods=['GET'])
    def index():
        """Rota principal com informações da API."""
        return jsonify({
            'name': 'ProjectFlow Gantt API',
            'version': '1.0.0',
            'description': 'API REST para gerenciamento de projetos com Gantt',
            'endpoints': {
                'projects': {
                    'GET /api/projects': 'Lista todos os projetos',
                    'POST /api/projects': 'Cria um novo projeto',
                    'GET /api/projects/<id>': 'Obtém um projeto',
                    'PUT /api/projects/<id>': 'Atualiza um projeto',
                    'DELETE /api/projects/<id>': 'Deleta um projeto',
                    'GET /api/projects/<id>/tasks': 'Lista tarefas do projeto'
                },
                'tasks': {
                    'GET /api/tasks': 'Lista todas as tarefas',
                    'POST /api/tasks': 'Cria uma nova tarefa',
                    'GET /api/tasks/<id>': 'Obtém uma tarefa',
                    'PUT /api/tasks/<id>': 'Atualiza uma tarefa',
                    'DELETE /api/tasks/<id>': 'Deleta uma tarefa'
                },
                'dashboard': {
                    'GET /api/dashboard': 'Métricas do dashboard'
                },
                'health': {
                    'GET /health': 'Status da API'
                }
            }
        })

    # Error handlers globais
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Recurso não encontrado'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500

    return app


def main():
    """Função principal para iniciar o servidor."""
    # Inicializa o banco de dados
    print("=" * 50)
    print("ProjectFlow Gantt - Inicializando...")
    print("=" * 50)

    try:
        # Cria as tabelas se não existirem
        print("\n[1/3] Inicializando banco de dados...")
        init_database()

        # Inicializa o pool de conexões
        print("\n[2/3] Configurando pool de conexões...")
        Database.init_pool()

        # Cria a aplicação
        print("\n[3/3] Iniciando servidor Flask...")
        app = create_app()

        # Configurações do servidor
        host = os.environ.get('FLASK_HOST', '0.0.0.0')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = app.config.get('DEBUG', False)

        print("\n" + "=" * 50)
        print(f"Servidor rodando em: http://{host}:{port}")
        print(f"Modo: {'Desenvolvimento' if debug else 'Produção'}")
        print("Pressione CTRL+C para parar")
        print("=" * 50 + "\n")

        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        print("\n\nServidor encerrado pelo usuário")
        Database.close_pool()
        sys.exit(0)
    except Exception as e:
        print(f"\nErro fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
