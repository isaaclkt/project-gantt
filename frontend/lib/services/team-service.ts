/**
 * Team Service Layer
 * Connected to Flask Backend API
 */

import { TeamMember, ApiResponse, CreateTeamMemberInput, UpdateTeamMemberInput } from '../types'
import { apiFetch } from '../api-config'

/**
 * Fetch all team members
 */
export async function getTeamMembers(): Promise<ApiResponse<TeamMember[]>> {
  const response = await apiFetch<{ data: TeamMember[]; success: boolean; pagination?: any }>('/team');
  return {
    data: response.data,
    success: response.success
  };
}

/**
 * Fetch a single team member by ID
 */
export async function getTeamMemberById(id: string): Promise<ApiResponse<TeamMember | null>> {
  try {
    const response = await apiFetch<ApiResponse<TeamMember>>(`/team/${id}`);
    return response;
  } catch (error) {
    return {
      data: null,
      success: false,
      message: 'Team member not found'
    };
  }
}

/**
 * Create a new team member
 */
export async function createTeamMember(input: CreateTeamMemberInput): Promise<ApiResponse<TeamMember>> {
  const response = await apiFetch<ApiResponse<TeamMember>>('/team', {
    method: 'POST',
    body: JSON.stringify(input),
  });
  return response;
}

/**
 * Update an existing team member
 */
export async function updateTeamMember(input: UpdateTeamMemberInput): Promise<ApiResponse<TeamMember | null>> {
  const { id, ...data } = input;
  const response = await apiFetch<ApiResponse<TeamMember>>(`/team/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response;
}

/**
 * Delete a team member
 */
export async function deleteTeamMember(id: string): Promise<ApiResponse<boolean>> {
  const response = await apiFetch<ApiResponse<null>>(`/team/${id}`, {
    method: 'DELETE',
  });
  return {
    data: response.success,
    success: response.success,
    message: response.message
  };
}
