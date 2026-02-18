-- ============================================
-- Migration: Add share_links table
-- ============================================

USE project_grantt;

-- Create share_links table for secure project sharing
CREATE TABLE IF NOT EXISTS share_links (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    project_id VARCHAR(36) NOT NULL,
    token VARCHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_share_links_token (token),
    INDEX idx_share_links_project (project_id),
    INDEX idx_share_links_expires (expires_at)
) ENGINE=InnoDB;
