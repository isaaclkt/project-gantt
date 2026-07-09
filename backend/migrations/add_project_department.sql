-- Migration: Add explicit department_id to projects
-- Date: 2026-07-09
--
-- Previously a project's department was derived indirectly from its owner's
-- department. This makes it explicit so a project can be scoped to a department
-- independently of who owns it (and survives owner removal / re-assignment).

-- 1. Add the column
ALTER TABLE projects
ADD COLUMN department_id VARCHAR(36) NULL AFTER owner_id,
ADD CONSTRAINT fk_projects_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

-- 2. Index for department-scoped listings
CREATE INDEX idx_projects_department_id ON projects(department_id);

-- 3. Backfill existing projects from their owner's department
UPDATE projects p
JOIN users u ON p.owner_id = u.id
SET p.department_id = u.department_id
WHERE p.department_id IS NULL
  AND u.department_id IS NOT NULL;
