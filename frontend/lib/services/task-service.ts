/**
 * Task Service Layer
 * Connected to Flask Backend API
 */

import { Task, CreateTaskInput, UpdateTaskInput, ApiResponse } from '../types'
import { apiFetch } from '../api-config'

/**
 * Fetch all tasks
 */
export async function getTasks(): Promise<ApiResponse<Task[]>> {
  const response = await apiFetch<{ data: Task[]; success: boolean; pagination?: any }>('/tasks');
  return {
    data: response.data,
    success: response.success
  };
}

/**
 * Fetch a single task by ID
 */
export async function getTaskById(id: string): Promise<ApiResponse<Task | null>> {
  try {
    const response = await apiFetch<ApiResponse<Task>>(`/tasks/${id}`);
    return response;
  } catch (error) {
    return {
      data: null,
      success: false,
      message: 'Task not found'
    };
  }
}

/**
 * Fetch tasks by project ID
 */
export async function getTasksByProject(projectId: string): Promise<ApiResponse<Task[]>> {
  const response = await apiFetch<ApiResponse<Task[]>>(`/projects/${projectId}/tasks`);
  return response;
}

/**
 * Create a new task
 */
export async function createTask(input: CreateTaskInput): Promise<ApiResponse<Task>> {
  const response = await apiFetch<ApiResponse<Task>>('/tasks', {
    method: 'POST',
    body: JSON.stringify(input),
  });
  return response;
}

/**
 * Update an existing task
 */
export async function updateTask(input: UpdateTaskInput): Promise<ApiResponse<Task>> {
  const { id, ...data } = input;
  const response = await apiFetch<ApiResponse<Task>>(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
  return response;
}

/**
 * Delete a task
 */
export async function deleteTask(id: string): Promise<ApiResponse<null>> {
  const response = await apiFetch<ApiResponse<null>>(`/tasks/${id}`, {
    method: 'DELETE',
  });
  return response;
}

/**
 * Reset tasks - not needed with real backend
 */
export function resetTasks(): void {
  // No-op with real backend
}
