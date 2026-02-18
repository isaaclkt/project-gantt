-- =============================================
-- Migration: Add audit logs and invites tables
-- Also add tracking fields to share_links
-- =============================================

USE project_grantt;

-- =============================================
-- Add tracking fields to share_links
-- =============================================
ALTER TABLE share_links
ADD COLUMN revoked_at TIMESTAMP NULL AFTER created_at,
ADD COLUMN last_access_at TIMESTAMP NULL AFTER revoked_at,
ADD COLUMN access_count INT DEFAULT 0 AFTER last_access_at;

-- Add index for revoked_at filtering
CREATE INDEX idx_share_links_revoked ON share_links(revoked_at);


-- =============================================
-- AUDIT LOGS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(36),
    details JSON DEFAULT ({}),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_resource_type (resource_type),
    INDEX idx_audit_logs_created_at (created_at),
    INDEX idx_audit_logs_resource (resource_type, resource_id),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- =============================================
-- INVITES TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS invites (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    token VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    department_id VARCHAR(36),
    password VARCHAR(255),
    created_by VARCHAR(36),
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    revoked_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_invites_token (token),
    INDEX idx_invites_email (email),
    INDEX idx_invites_expires_at (expires_at),
    INDEX idx_invites_created_at (created_at),
    INDEX idx_invites_department (department_id),

    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- END OF MIGRATION
-- =============================================
