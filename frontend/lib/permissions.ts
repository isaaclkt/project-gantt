/**
 * Frontend permission helpers - mirrors backend RBAC model
 */

type UserRole = 'admin' | 'manager' | 'member' | 'viewer'

// --- Project permissions ---

export function canCreateProject(role: UserRole): boolean {
  return role === 'admin' || role === 'manager'
}

export function canEditProject(role: UserRole): boolean {
  return role === 'admin' || role === 'manager'
}

export function canDeleteProject(role: UserRole): boolean {
  return role === 'admin'
}

// --- Task permissions ---

export function canCreateTask(role: UserRole): boolean {
  return role === 'admin' || role === 'manager' || role === 'member'
}

export function canEditTask(role: UserRole): boolean {
  return role === 'admin' || role === 'manager' || role === 'member'
}

export function canDeleteTask(role: UserRole): boolean {
  return role === 'admin' || role === 'manager'
}

// --- Team permissions ---

export function canManageTeam(role: UserRole): boolean {
  return role === 'admin' || role === 'manager'
}
