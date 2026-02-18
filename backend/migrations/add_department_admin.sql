-- Migration: Add department admin functionality
-- Date: 2026-02-17

-- 1. Add admin_id column to departments table
ALTER TABLE departments
ADD COLUMN admin_id VARCHAR(36) UNIQUE,
ADD CONSTRAINT fk_department_admin
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL;

-- 2. Update users role ENUM to include 'department_admin'
-- Note: MySQL requires recreating the column to modify ENUM values
ALTER TABLE users
MODIFY COLUMN role ENUM('admin', 'department_admin', 'manager', 'member', 'viewer') DEFAULT 'member';

-- 3. Create index for faster lookups
CREATE INDEX idx_departments_admin_id ON departments(admin_id);
