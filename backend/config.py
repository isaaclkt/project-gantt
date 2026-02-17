"""
Configurações da aplicação Flask.
Credenciais do banco de dados e outras configurações.
"""
import os


class Config:
    """Configurações base da aplicação."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False

    # MySQL Database
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'projectflow_gantt'

    # Pool de conexões
    DB_POOL_SIZE = 5
    DB_POOL_TIMEOUT = 30


class DevelopmentConfig(Config):
    """Configurações de desenvolvimento."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurações de produção."""
    DEBUG = False


class TestingConfig(Config):
    """Configurações de teste."""
    DEBUG = True
    DB_NAME = 'projectflow_gantt_test'


# Mapeamento de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retorna a configuração baseada na variável de ambiente."""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, config['default'])
