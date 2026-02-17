/**
 * Admin Service Layer
 * Manages departments and roles
 */

import { ApiResponse } from '../types'
import { apiFetch } from '../api-config'

export interface Department {
  id: string
  name: string
  description?: string
  createdAt: string
}

export interface Role {
  id: string
  name: string
  description?: string
  createdAt: string
}

export interface CreateDepartmentInput {
  name: string
  description?: string
}

export interface CreateRoleInput {
  name: string
  description?: string
}

// ============================================
// Departments
// ============================================

export async function getDepartments(): Promise<ApiResponse<Department[]>> {
  const response = await apiFetch<ApiResponse<Department[]>>('/admin/departments')
  return response
}

export async function createDepartment(input: CreateDepartmentInput): Promise<ApiResponse<Department>> {
  const response = await apiFetch<ApiResponse<Department>>('/admin/departments', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return response
}

export async function updateDepartment(id: string, input: Partial<CreateDepartmentInput>): Promise<ApiResponse<Department>> {
  const response = await apiFetch<ApiResponse<Department>>(`/admin/departments/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
  return response
}

export async function deleteDepartment(id: string): Promise<ApiResponse<null>> {
  const response = await apiFetch<ApiResponse<null>>(`/admin/departments/${id}`, {
    method: 'DELETE',
  })
  return response
}

// ============================================
// Roles
// ============================================

export async function getRoles(): Promise<ApiResponse<Role[]>> {
  const response = await apiFetch<ApiResponse<Role[]>>('/admin/roles')
  return response
}

export async function createRole(input: CreateRoleInput): Promise<ApiResponse<Role>> {
  const response = await apiFetch<ApiResponse<Role>>('/admin/roles', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return response
}

export async function updateRole(id: string, input: Partial<CreateRoleInput>): Promise<ApiResponse<Role>> {
  const response = await apiFetch<ApiResponse<Role>>(`/admin/roles/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
  return response
}

export async function deleteRole(id: string): Promise<ApiResponse<null>> {
  const response = await apiFetch<ApiResponse<null>>(`/admin/roles/${id}`, {
    method: 'DELETE',
  })
  return response
}
