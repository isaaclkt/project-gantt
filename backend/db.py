"""
Módulo de conexão com o banco de dados MySQL.
Implementa pool de conexões para melhor performance.
"""
import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from config import get_config


class Database:
    """Gerenciador de conexões do banco de dados MySQL."""

    _pool = None

    @classmethod
    def init_pool(cls):
        """Inicializa o pool de conexões."""
        if cls._pool is None:
            config = get_config()
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="projectflow_pool",
                    pool_size=config.DB_POOL_SIZE,
                    pool_reset_session=True,
                    host=config.DB_HOST,
                    port=config.DB_PORT,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci',
                    autocommit=False
                )
                print(f"Pool de conexões inicializado: {config.DB_NAME}")
            except Error as e:
                print(f"Erro ao criar pool de conexões: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Obtém uma conexão do pool."""
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.get_connection()

    @classmethod
    @contextmanager
    def get_cursor(cls, dictionary=True):
        """
        Context manager para obter cursor com commit/rollback automático.

        Args:
            dictionary: Se True, retorna resultados como dicionários.

        Yields:
            cursor: Cursor do MySQL.
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
            connection.commit()
        except Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=True):
        """
        Executa uma query SELECT.

        Args:
            query: Query SQL (usar %s para parâmetros).
            params: Tupla com parâmetros da query.
            fetch_one: Se True, retorna apenas um registro.
            fetch_all: Se True, retorna todos os registros.

        Returns:
            Resultado da query ou None.
        """
        with cls.get_cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return None

    @classmethod
    def execute_insert(cls, query, params=None):
        """
        Executa uma query INSERT.

        Args:
            query: Query SQL INSERT.
            params: Tupla com parâmetros.

        Returns:
            ID do registro inserido.
        """
        with cls.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid

    @classmethod
    def execute_update(cls, query, params=None):
        """
        Executa uma query UPDATE ou DELETE.

        Args:
            query: Query SQL UPDATE/DELETE.
            params: Tupla com parâmetros.

        Returns:
            Número de linhas afetadas.
        """
        with cls.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount

    @classmethod
    def close_pool(cls):
        """Fecha todas as conexões do pool."""
        if cls._pool:
            # MySQL Connector não tem método close() para pool
            # As conexões são fechadas quando retornadas
            cls._pool = None
            print("Pool de conexões fechado")


def init_database():
    """Inicializa o banco de dados e cria as tabelas se necessário."""
    config = get_config()

    # Conecta sem especificar database para criar se não existir
    try:
        connection = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        cursor = connection.cursor()

        # Cria o database se não existir
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE {config.DB_NAME}")

        # Cria tabela de projetos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_name (name),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        # Cria tabela de tarefas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status ENUM('todo', 'doing', 'review', 'done') DEFAULT 'todo',
                assignee VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                INDEX idx_project_id (project_id),
                INDEX idx_status (status),
                INDEX idx_dates (start_date, end_date),
                CONSTRAINT chk_dates CHECK (start_date <= end_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        connection.commit()
        print(f"Banco de dados '{config.DB_NAME}' inicializado com sucesso!")

    except Error as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
