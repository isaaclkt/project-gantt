-- ============================================
-- ProjectFlow Gantt - Database Schema
-- Sistema de Gerenciamento de Projetos
-- ============================================

-- Cria o banco de dados
CREATE DATABASE IF NOT EXISTS projectflow_gantt
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE projectflow_gantt;

-- ============================================
-- Tabela: projects
-- Armazena os projetos do sistema
-- ============================================
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT 'Nome do projeto',
    description TEXT COMMENT 'Descrição detalhada do projeto',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de criação',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Data da última atualização',

    -- Índices para performance
    INDEX idx_name (name),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabela de projetos';

-- ============================================
-- Tabela: tasks
-- Armazena as tarefas dos projetos
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT 'ID do projeto relacionado',
    name VARCHAR(255) NOT NULL COMMENT 'Nome da tarefa',
    start_date DATE NOT NULL COMMENT 'Data de início',
    end_date DATE NOT NULL COMMENT 'Data de término',
    status ENUM('todo', 'doing', 'review', 'done') DEFAULT 'todo' COMMENT 'Status da tarefa',
    assignee VARCHAR(100) COMMENT 'Responsável pela tarefa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Data de criação',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Data da última atualização',

    -- Chave estrangeira com CASCADE
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,

    -- Índices para performance
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_assignee (assignee),

    -- Constraint para garantir que início <= fim
    CONSTRAINT chk_dates CHECK (start_date <= end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabela de tarefas dos projetos';

-- ============================================
-- Dados de exemplo (opcional)
-- ============================================

-- Projeto de exemplo 1
INSERT INTO projects (name, description) VALUES
('Redesign do Website', 'Projeto de redesign completo do website corporativo com foco em UX/UI moderna'),
('App Mobile E-commerce', 'Desenvolvimento do aplicativo mobile para a plataforma de e-commerce'),
('Sistema de Gestão Interna', 'ERP interno para gestão de recursos humanos e financeiros');

-- Tarefas do Projeto 1 (Redesign do Website)
INSERT INTO tasks (project_id, name, start_date, end_date, status, assignee) VALUES
(1, 'Análise de requisitos', '2024-01-15', '2024-01-22', 'done', 'Maria Silva'),
(1, 'Wireframes e protótipos', '2024-01-23', '2024-02-05', 'done', 'Carlos Santos'),
(1, 'Design de UI', '2024-02-06', '2024-02-20', 'doing', 'Ana Costa'),
(1, 'Desenvolvimento Frontend', '2024-02-21', '2024-03-15', 'todo', 'João Oliveira'),
(1, 'Testes e QA', '2024-03-16', '2024-03-25', 'todo', 'Pedro Lima'),
(1, 'Deploy e lançamento', '2024-03-26', '2024-03-31', 'todo', 'Maria Silva');

-- Tarefas do Projeto 2 (App Mobile)
INSERT INTO tasks (project_id, name, start_date, end_date, status, assignee) VALUES
(2, 'Definição de arquitetura', '2024-02-01', '2024-02-10', 'done', 'Lucas Ferreira'),
(2, 'Setup do projeto React Native', '2024-02-11', '2024-02-15', 'done', 'Lucas Ferreira'),
(2, 'Tela de login e cadastro', '2024-02-16', '2024-02-28', 'review', 'Fernanda Souza'),
(2, 'Catálogo de produtos', '2024-03-01', '2024-03-20', 'doing', 'Rafael Mendes'),
(2, 'Carrinho de compras', '2024-03-21', '2024-04-05', 'todo', 'Fernanda Souza'),
(2, 'Integração com pagamentos', '2024-04-06', '2024-04-20', 'todo', 'Lucas Ferreira');

-- Tarefas do Projeto 3 (Sistema de Gestão)
INSERT INTO tasks (project_id, name, start_date, end_date, status, assignee) VALUES
(3, 'Levantamento de processos', '2024-01-10', '2024-01-25', 'done', 'Mariana Rocha'),
(3, 'Modelagem do banco de dados', '2024-01-26', '2024-02-08', 'done', 'Bruno Alves'),
(3, 'Módulo de RH', '2024-02-09', '2024-03-10', 'doing', 'Camila Dias'),
(3, 'Módulo Financeiro', '2024-03-11', '2024-04-15', 'todo', 'Bruno Alves'),
(3, 'Relatórios e dashboards', '2024-04-16', '2024-05-01', 'todo', 'Mariana Rocha');

-- ============================================
-- Views úteis (opcional)
-- ============================================

-- View: Resumo de projetos com progresso
CREATE OR REPLACE VIEW vw_project_summary AS
SELECT
    p.id,
    p.name,
    p.description,
    p.created_at,
    COUNT(t.id) as total_tasks,
    SUM(CASE WHEN t.status = 'todo' THEN 1 ELSE 0 END) as todo_count,
    SUM(CASE WHEN t.status = 'doing' THEN 1 ELSE 0 END) as doing_count,
    SUM(CASE WHEN t.status = 'review' THEN 1 ELSE 0 END) as review_count,
    SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as done_count,
    ROUND(
        (SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) / COUNT(t.id)) * 100, 1
    ) as progress_percent
FROM projects p
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id;

-- View: Tarefas atrasadas
CREATE OR REPLACE VIEW vw_overdue_tasks AS
SELECT
    t.id,
    t.name as task_name,
    p.name as project_name,
    t.end_date,
    DATEDIFF(CURDATE(), t.end_date) as days_overdue,
    t.assignee,
    t.status
FROM tasks t
JOIN projects p ON t.project_id = p.id
WHERE t.end_date < CURDATE() AND t.status != 'done'
ORDER BY days_overdue DESC;

-- ============================================
-- Comandos úteis
-- ============================================

-- Listar todos os projetos com progresso:
-- SELECT * FROM vw_project_summary;

-- Listar tarefas atrasadas:
-- SELECT * FROM vw_overdue_tasks;

-- Métricas do dashboard:
-- SELECT
--     COUNT(*) as total_tasks,
--     SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo,
--     SUM(CASE WHEN status = 'doing' THEN 1 ELSE 0 END) as doing,
--     SUM(CASE WHEN status = 'review' THEN 1 ELSE 0 END) as review,
--     SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
-- FROM tasks;
