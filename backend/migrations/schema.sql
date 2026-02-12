-- ============================================
-- Project Grantt - Database Schema
-- MySQL 8.0+
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS project_grantt
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE project_grantt;

-- ============================================
-- Drop tables if exist (for clean recreation)
-- ============================================
DROP TABLE IF EXISTS project_members;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS users;

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    role VARCHAR(100) DEFAULT 'member',
    department VARCHAR(100),
    phone VARCHAR(50),
    timezone VARCHAR(100) DEFAULT 'America/Sao_Paulo',
    status ENUM('active', 'away', 'offline') DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_users_email (email),
    INDEX idx_users_status (status),
    INDEX idx_users_department (department)
) ENGINE=InnoDB;

-- ============================================
-- USER SETTINGS TABLE
-- ============================================
CREATE TABLE user_settings (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL UNIQUE,
    theme ENUM('light', 'dark', 'system') DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'pt-BR',

    -- Notification preferences (stored as JSON for flexibility)
    notifications JSON DEFAULT ('{"email": true, "push": true, "taskReminders": true, "projectUpdates": true}'),

    -- Display preferences
    display_preferences JSON DEFAULT ('{"compactMode": false, "showAvatars": true, "defaultView": "gantt"}'),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_settings_user (user_id)
) ENGINE=InnoDB;

-- ============================================
-- TEAM MEMBERS TABLE (for team management view)
-- ============================================
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    avatar VARCHAR(500),
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    status ENUM('active', 'away', 'offline') DEFAULT 'active',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_team_members_email (email),
    INDEX idx_team_members_status (status),
    INDEX idx_team_members_department (department)
) ENGINE=InnoDB;

-- ============================================
-- PROJECTS TABLE
-- ============================================
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3B82F6',
    status ENUM('planning', 'active', 'on-hold', 'completed') DEFAULT 'planning',
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    owner_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_projects_status (status),
    INDEX idx_projects_owner (owner_id),
    INDEX idx_projects_dates (start_date, end_date)
) ENGINE=InnoDB;

-- ============================================
-- PROJECT MEMBERS TABLE (many-to-many relationship)
-- ============================================
CREATE TABLE project_members (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id VARCHAR(36) NOT NULL,
    team_member_id VARCHAR(36) NOT NULL,
    role VARCHAR(100) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (team_member_id) REFERENCES team_members(id) ON DELETE CASCADE,
    UNIQUE KEY unique_project_member (project_id, team_member_id),
    INDEX idx_project_members_project (project_id),
    INDEX idx_project_members_member (team_member_id)
) ENGINE=InnoDB;

-- ============================================
-- TASKS TABLE
-- ============================================
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('todo', 'in-progress', 'review', 'completed') DEFAULT 'todo',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    assignee_id VARCHAR(36),
    project_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (assignee_id) REFERENCES team_members(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_project (project_id),
    INDEX idx_tasks_assignee (assignee_id),
    INDEX idx_tasks_dates (start_date, end_date)
) ENGINE=InnoDB;

-- ============================================
-- STORED PROCEDURES
-- ============================================

-- Procedure to update project progress based on tasks
DELIMITER //
CREATE PROCEDURE update_project_progress(IN p_project_id VARCHAR(36))
BEGIN
    UPDATE projects
    SET progress = (
        SELECT COALESCE(AVG(progress), 0)
        FROM tasks
        WHERE project_id = p_project_id
    )
    WHERE id = p_project_id;
END //
DELIMITER ;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger to auto-update project progress when task is updated
DELIMITER //
CREATE TRIGGER after_task_update
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    CALL update_project_progress(NEW.project_id);
END //
DELIMITER ;

-- Trigger to auto-update project progress when task is inserted
DELIMITER //
CREATE TRIGGER after_task_insert
AFTER INSERT ON tasks
FOR EACH ROW
BEGIN
    CALL update_project_progress(NEW.project_id);
END //
DELIMITER ;

-- Trigger to auto-update project progress when task is deleted
DELIMITER //
CREATE TRIGGER after_task_delete
AFTER DELETE ON tasks
FOR EACH ROW
BEGIN
    CALL update_project_progress(OLD.project_id);
END //
DELIMITER ;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert sample users
INSERT INTO users (id, name, email, password_hash, avatar, role, department, timezone) VALUES
('u1', 'Ana Silva', 'ana.silva@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Ana', 'Project Manager', 'Gestão', 'America/Sao_Paulo'),
('u2', 'Carlos Santos', 'carlos.santos@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos', 'Frontend Developer', 'Desenvolvimento', 'America/Sao_Paulo'),
('u3', 'Marina Costa', 'marina.costa@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marina', 'Backend Developer', 'Desenvolvimento', 'America/Sao_Paulo'),
('u4', 'Pedro Oliveira', 'pedro.oliveira@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Pedro', 'UI/UX Designer', 'Design', 'America/Sao_Paulo'),
('u5', 'Julia Ferreira', 'julia.ferreira@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Julia', 'QA Engineer', 'Qualidade', 'America/Sao_Paulo'),
('u6', 'Rafael Mendes', 'rafael.mendes@empresa.com', '$2b$12$placeholder_hash', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rafael', 'DevOps Engineer', 'Infraestrutura', 'America/Sao_Paulo');

-- Insert user settings for sample users
INSERT INTO user_settings (user_id, theme, language) VALUES
('u1', 'dark', 'pt-BR'),
('u2', 'system', 'pt-BR'),
('u3', 'light', 'pt-BR'),
('u4', 'dark', 'pt-BR'),
('u5', 'system', 'pt-BR'),
('u6', 'dark', 'pt-BR');

-- Insert team members
INSERT INTO team_members (id, user_id, name, email, avatar, role, department, status) VALUES
('tm1', 'u1', 'Ana Silva', 'ana.silva@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Ana', 'Project Manager', 'Gestão', 'active'),
('tm2', 'u2', 'Carlos Santos', 'carlos.santos@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos', 'Frontend Developer', 'Desenvolvimento', 'active'),
('tm3', 'u3', 'Marina Costa', 'marina.costa@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marina', 'Backend Developer', 'Desenvolvimento', 'away'),
('tm4', 'u4', 'Pedro Oliveira', 'pedro.oliveira@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Pedro', 'UI/UX Designer', 'Design', 'active'),
('tm5', 'u5', 'Julia Ferreira', 'julia.ferreira@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Julia', 'QA Engineer', 'Qualidade', 'offline'),
('tm6', 'u6', 'Rafael Mendes', 'rafael.mendes@empresa.com', 'https://api.dicebear.com/7.x/avataaars/svg?seed=Rafael', 'DevOps Engineer', 'Infraestrutura', 'active');

-- Insert sample projects
INSERT INTO projects (id, name, description, color, status, progress, start_date, end_date, owner_id) VALUES
('p1', 'Website Redesign', 'Redesign completo do website corporativo', '#3B82F6', 'active', 65, DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_ADD(CURDATE(), INTERVAL 20 DAY), 'u1'),
('p2', 'Mobile App', 'Desenvolvimento do aplicativo mobile', '#10B981', 'active', 35, DATE_SUB(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 30 DAY), 'u1'),
('p3', 'API Integration', 'Integração com APIs de terceiros', '#F59E0B', 'planning', 10, DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 25 DAY), 'u3'),
('p4', 'Security Audit', 'Auditoria de segurança do sistema', '#EF4444', 'on-hold', 20, DATE_SUB(CURDATE(), INTERVAL 15 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'u6'),
('p5', 'Documentation Update', 'Atualização da documentação técnica', '#8B5CF6', 'completed', 100, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 5 DAY), 'u1');

-- Insert project members
INSERT INTO project_members (project_id, team_member_id, role) VALUES
('p1', 'tm1', 'owner'),
('p1', 'tm2', 'member'),
('p1', 'tm4', 'member'),
('p2', 'tm1', 'owner'),
('p2', 'tm2', 'member'),
('p2', 'tm3', 'member'),
('p3', 'tm3', 'owner'),
('p3', 'tm6', 'member'),
('p4', 'tm6', 'owner'),
('p4', 'tm5', 'member'),
('p5', 'tm1', 'owner'),
('p5', 'tm5', 'member');

-- Insert sample tasks
INSERT INTO tasks (id, name, description, start_date, end_date, status, priority, progress, assignee_id, project_id) VALUES
('t1', 'Design da Homepage', 'Criar novo design da página inicial', DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_SUB(CURDATE(), INTERVAL 3 DAY), 'completed', 'high', 100, 'tm4', 'p1'),
('t2', 'Implementação Frontend', 'Desenvolver componentes React', DATE_SUB(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'in-progress', 'high', 60, 'tm2', 'p1'),
('t3', 'Revisão de Código', 'Code review do frontend', DATE_ADD(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'todo', 'medium', 0, 'tm3', 'p1'),
('t4', 'Testes de Usabilidade', 'Realizar testes com usuários', DATE_ADD(CURDATE(), INTERVAL 8 DAY), DATE_ADD(CURDATE(), INTERVAL 12 DAY), 'todo', 'medium', 0, 'tm5', 'p1'),
('t5', 'Setup do Projeto Mobile', 'Configurar ambiente React Native', DATE_SUB(CURDATE(), INTERVAL 5 DAY), DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'completed', 'high', 100, 'tm2', 'p2'),
('t6', 'Desenvolvimento de Telas', 'Criar telas principais do app', DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'in-progress', 'high', 30, 'tm2', 'p2'),
('t7', 'API Backend Mobile', 'Desenvolver endpoints para o app', DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'review', 'high', 80, 'tm3', 'p2'),
('t8', 'Análise de Requisitos', 'Levantar requisitos de integração', DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'todo', 'medium', 0, 'tm3', 'p3'),
('t9', 'Scan de Vulnerabilidades', 'Executar ferramentas de scan', DATE_SUB(CURDATE(), INTERVAL 15 DAY), DATE_SUB(CURDATE(), INTERVAL 10 DAY), 'completed', 'high', 100, 'tm6', 'p4'),
('t10', 'Relatório de Segurança', 'Documentar vulnerabilidades encontradas', DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'in-progress', 'high', 40, 'tm6', 'p4');

-- ============================================
-- VIEWS (Optional - for convenience)
-- ============================================

-- View for tasks with project and assignee info
CREATE VIEW v_tasks_detailed AS
SELECT
    t.id,
    t.name,
    t.description,
    t.start_date,
    t.end_date,
    t.status,
    t.priority,
    t.progress,
    t.project_id,
    p.name AS project_name,
    p.color AS project_color,
    t.assignee_id,
    tm.name AS assignee_name,
    tm.avatar AS assignee_avatar,
    t.created_at,
    t.updated_at
FROM tasks t
LEFT JOIN projects p ON t.project_id = p.id
LEFT JOIN team_members tm ON t.assignee_id = tm.id;

-- View for projects with member count
CREATE VIEW v_projects_summary AS
SELECT
    p.*,
    COUNT(DISTINCT pm.team_member_id) AS member_count,
    COUNT(DISTINCT t.id) AS task_count,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) AS completed_tasks
FROM projects p
LEFT JOIN project_members pm ON p.id = pm.project_id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id;
