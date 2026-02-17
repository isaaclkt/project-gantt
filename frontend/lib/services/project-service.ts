/**
 * Project Service Layer
 * Connected to Flask Backend API
 */

import { Project, ApiResponse, CreateProjectInput, UpdateProjectInput } from '../types'
import { apiFetch } from '../api-config'

/**
 * Fetch all projects
 */
export async function getProjects(): Promise<ApiResponse<Project[]>> {
  const response = await apiFetch<{ data: Project[]; success: boolean; pagination?: any }>('/projects');
  return {
    data: response.data,
    success: response.success
  };
}

/**
 * Fetch a single project by ID
 */
export async function getProjectById(id: string): Promise<ApiResponse<Project | null>> {
  try {
    const response = await apiFetch<ApiResponse<Project>>(`/projects/${id}`);
    return response;
  } catch (error) {
    return {
      data: null,
      success: false,
      message: 'Project not found'
    };
  }
}

/**
 * Create a new project
 */
export async function createProject(input: CreateProjectInput): Promise<ApiResponse<Project>> {
  const response = await apiFetch<ApiResponse<Project>>('/projects', {
    method: 'POST',
    body: JSON.stringify(input),
  });
  return response;
}

/**
 * Update an existing project
 */
export async function updateProject(input: UpdateProjectInput): Promise<ApiResponse<Project | null>> {
  const { id, ...data } = input;
  const response = await apiFetch<ApiResponse<Project>>(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response;
}

/**
 * Delete a project
 */
export async function deleteProject(id: string): Promise<ApiResponse<boolean>> {
  const response = await apiFetch<ApiResponse<null>>(`/projects/${id}`, {
    method: 'DELETE',
  });
  return {
    data: response.success,
    success: response.success,
    message: response.message
  };
}
