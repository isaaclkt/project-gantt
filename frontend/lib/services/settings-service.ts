/**
 * Settings Service Layer
 * Connected to Flask Backend API
 */

import { UserSettings, UserProfile, ApiResponse } from '../types'
import { apiFetch } from '../api-config'

/**
 * Fetch user profile
 */
export async function getUserProfile(): Promise<ApiResponse<UserProfile>> {
  const response = await apiFetch<ApiResponse<UserProfile>>('/user/profile');
  return response;
}

/**
 * Update user profile
 */
export async function updateUserProfile(
  updates: Partial<Omit<UserProfile, 'id' | 'joinedAt'>>
): Promise<ApiResponse<UserProfile>> {
  const response = await apiFetch<ApiResponse<UserProfile>>('/user/profile', {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
  return response;
}

/**
 * Fetch user settings
 */
export async function getUserSettings(): Promise<ApiResponse<UserSettings>> {
  const response = await apiFetch<ApiResponse<UserSettings>>('/user/settings');
  return response;
}

/**
 * Update user settings
 */
export async function updateUserSettings(
  updates: Partial<Omit<UserSettings, 'id' | 'userId'>>
): Promise<ApiResponse<UserSettings>> {
  const response = await apiFetch<ApiResponse<UserSettings>>('/user/settings', {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
  return response;
}

/**
 * Change user password
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<ApiResponse<null>> {
  const response = await apiFetch<ApiResponse<null>>('/auth/change-password', {
    method: 'POST',
    body: JSON.stringify({ currentPassword, newPassword }),
  });
  return response;
}

/**
 * Upload user avatar
 */
export async function uploadAvatar(file: File): Promise<ApiResponse<UserProfile>> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiFetch<ApiResponse<UserProfile>>('/user/avatar', {
    method: 'POST',
    body: formData,
  });
  return response;
}
