-- =============================================
-- ProjectFlow - Database Schema
-- MySQL 8.0+ | Complete schema with all tables
-- =============================================

-- Create database
CREATE DATABASE IF NOT EXISTS project_grantt
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE project_grantt;

-- =============================================
-- Drop existing objects (in correct order)
-- =============================================
DROP VIEW IF EXISTS v_tasks_detailed;
DROP VIEW IF EXISTS v_projects_summary;
DROP TRIGGER IF EXISTS after_task_update;
DROP TRIGGER IF EXISTS after_task_insert;
DROP TRIGGER IF EXISTS after_task_delete;
DROP PROCEDURE IF EXISTS update_project_progress;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS share_links;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS project_members;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS user_settings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS departments;
SET FOREIGN_KEY_CHECKS = 1;

-- =============================================
-- DEPARTMENTS TABLE
-- =============================================
CREATE TABLE departments (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    admin_id VARCHAR(36) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_departments_name (name),
    INDEX idx_departments_admin_id (admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- ROLES TABLE (job titles/positions)
-- =============================================
CREATE TABLE roles (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_roles_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- USERS TABLE
-- Roles: admin, department_admin, manager, member, viewer
-- =============================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar VARCHAR(500),
    role ENUM('admin', 'department_admin', 'manager', 'member', 'viewer') DEFAULT 'member',
    department_id VARCHAR(36),
    department VARCHAR(100),
    phone VARCHAR(50),
    timezone VARCHAR(100) DEFAULT 'America/Sao_Paulo',
    status ENUM('active', 'away', 'offline') DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,

    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_department_id (department_id),
    INDEX idx_users_is_active (is_active),
    INDEX idx_users_deleted (deleted_at),

    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add foreign key for department admin
ALTER TABLE departments
ADD CONSTRAINT fk_department_admin
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL;

-- =============================================
-- USER SETTINGS TABLE
-- =============================================
CREATE TABLE user_settings (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL UNIQUE,
    theme ENUM('light', 'dark', 'system') DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'pt-BR',
    notifications JSON DEFAULT ('{"email": true, "push": true, "taskReminders": true, "projectUpdates": true}'),
    display_preferences JSON DEFAULT ('{"compactMode": false, "showAvatars": true, "defaultView": "gantt"}'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TEAM MEMBERS TABLE
-- =============================================
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) UNIQUE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    avatar VARCHAR(500),
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    status ENUM('active', 'away', 'offline') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,

    INDEX idx_team_members_email (email),
    INDEX idx_team_members_department (department),
    INDEX idx_team_members_status (status),
    INDEX idx_team_members_deleted (deleted_at),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- PROJECTS TABLE
-- =============================================
CREATE TABLE projects (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(20) DEFAULT '#3B82F6',
    status ENUM('planning', 'active', 'on-hold', 'completed') DEFAULT 'planning',
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    owner_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,

    INDEX idx_projects_status (status),
    INDEX idx_projects_owner_id (owner_id),
    INDEX idx_projects_dates (start_date, end_date),
    INDEX idx_projects_deleted (deleted_at),

    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- PROJECT MEMBERS TABLE (Many-to-Many)
-- =============================================
CREATE TABLE project_members (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id VARCHAR(36) NOT NULL,
    team_member_id VARCHAR(36) NOT NULL,
    role VARCHAR(100) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_project_member (project_id, team_member_id),
    INDEX idx_project_members_project (project_id),
    INDEX idx_project_members_member (team_member_id),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (team_member_id) REFERENCES team_members(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TASKS TABLE
-- =============================================
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('todo', 'in-progress', 'review', 'completed') DEFAULT 'todo',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    project_id VARCHAR(36) NOT NULL,
    assignee_id VARCHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,

    INDEX idx_tasks_project_id (project_id),
    INDEX idx_tasks_assignee_id (assignee_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_dates (start_date, end_date),
    INDEX idx_tasks_deleted (deleted_at),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES team_members(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- SHARE LINKS TABLE
-- Temporary links for sharing project Gantt view
-- =============================================
CREATE TABLE share_links (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id VARCHAR(36) NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_share_links_token (token),
    INDEX idx_share_links_project (project_id),
    INDEX idx_share_links_expires (expires_at),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- STORED PROCEDURES
-- =============================================
DELIMITER //
CREATE PROCEDURE update_project_progress(IN p_project_id VARCHAR(36))
BEGIN
    UPDATE projects
    SET progress = (
        SELECT COALESCE(AVG(progress), 0)
        FROM tasks
        WHERE project_id = p_project_id AND deleted_at IS NULL
    )
    WHERE id = p_project_id;
END //
DELIMITER ;

-- =============================================
-- TRIGGERS
-- =============================================
DELIMITER //
CREATE TRIGGER after_task_update
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    IF NEW.deleted_at IS NULL THEN
        CALL update_project_progress(NEW.project_id);
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_task_insert
AFTER INSERT ON tasks
FOR EACH ROW
BEGIN
    CALL update_project_progress(NEW.project_id);
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_task_delete
AFTER DELETE ON tasks
FOR EACH ROW
BEGIN
    CALL update_project_progress(OLD.project_id);
END //
DELIMITER ;

-- =============================================
-- VIEWS
-- =============================================
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
LEFT JOIN team_members tm ON t.assignee_id = tm.id
WHERE t.deleted_at IS NULL;

CREATE VIEW v_projects_summary AS
SELECT
    p.*,
    COUNT(DISTINCT pm.team_member_id) AS member_count,
    COUNT(DISTINCT t.id) AS task_count,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) AS completed_tasks
FROM projects p
LEFT JOIN project_members pm ON p.id = pm.project_id
LEFT JOIN tasks t ON p.id = t.project_id AND t.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id;

-- =============================================
-- END OF SCHEMA
-- =============================================
