/**
 * Frontend permission helpers - mirrors backend RBAC model
 *
 * Role Hierarchy: ADMIN > DEPARTMENT_ADMIN > MANAGER > MEMBER > VIEWER
 */

import { UserRole } from './types'

// Role hierarchy for comparison
const ROLE_HIERARCHY: Record<UserRole, number> = {
  viewer: 0,
  member: 1,
  manager: 2,
  department_admin: 3,
  admin: 4,
}

/**
 * Check if a role has at least the required level
 */
export function hasMinRole(role: UserRole, minRole: UserRole): boolean {
  return ROLE_HIERARCHY[role] >= ROLE_HIERARCHY[minRole]
}

/**
 * Check if user is an admin (global or department)
 */
export function isAnyAdmin(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin'
}

// --- Project permissions ---

export function canCreateProject(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager'
}

export function canEditProject(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager'
}

export function canDeleteProject(role: UserRole): boolean {
  return role === 'admin'
}

export function canShareProject(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager'
}

// --- Task permissions ---

export function canCreateTask(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager' || role === 'member'
}

export function canEditTask(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager' || role === 'member'
}

export function canDeleteTask(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager'
}

// --- Team permissions ---

export function canManageTeam(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin' || role === 'manager'
}

/**
 * Check if user can manage department members
 * Note: department_admin can only manage their own department (checked server-side)
 */
export function canManageDepartmentMembers(role: UserRole): boolean {
  return role === 'admin' || role === 'department_admin'
}

// --- Admin permissions ---

export function canManageDepartments(role: UserRole): boolean {
  return role === 'admin'
}

export function canManageRoles(role: UserRole): boolean {
  return role === 'admin'
}

export function canAccessSystemSettings(role: UserRole): boolean {
  return role === 'admin'
}

/**
 * Get display name for a role
 */
export function getRoleDisplayName(role: UserRole): string {
  const names: Record<UserRole, string> = {
    admin: 'Administrador',
    department_admin: 'Admin de Departamento',
    manager: 'Gerente',
    member: 'Membro',
    viewer: 'Visualizador',
  }
  return names[role] || role
}
