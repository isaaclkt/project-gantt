/**
 * Share Link Service Layer
 */
import { ApiResponse } from '../types'
import { apiFetch } from '../api-config'

export interface ShareLink {
  id: string
  projectId: string
  token: string
  expiresAt: string
  createdBy: string
  createdAt: string
  isExpired: boolean
}

export interface CreateShareLinkInput {
  expiresInDays?: number
}

export interface SharedProject {
  id: string
  name: string
  description: string
  color: string
  status: string
  progress: number
  startDate: string
  endDate: string
  tasks: Array<{
    id: string
    name: string
    description: string
    startDate: string
    endDate: string
    status: string
    priority: string
    progress: number
    assigneeId?: string
  }>
  teamMembers: Array<{
    id: string
    name: string
    avatar: string
    role: string
  }>
}

/**
 * Create a share link for a project
 */
export async function createShareLink(
  projectId: string,
  input?: CreateShareLinkInput
): Promise<ApiResponse<ShareLink>> {
  const response = await apiFetch<ApiResponse<ShareLink>>(`/share/projects/${projectId}`, {
    method: 'POST',
    body: JSON.stringify(input || {}),
  })
  return response
}

/**
 * Get all share links for a project
 */
export async function getProjectShareLinks(projectId: string): Promise<ApiResponse<ShareLink[]>> {
  const response = await apiFetch<ApiResponse<ShareLink[]>>(`/share/projects/${projectId}/links`)
  return response
}

/**
 * Delete a share link
 */
export async function deleteShareLink(linkId: string): Promise<ApiResponse<null>> {
  const response = await apiFetch<ApiResponse<null>>(`/share/links/${linkId}`, {
    method: 'DELETE',
  })
  return response
}

/**
 * Get shared project (public, no auth needed)
 */
export async function getSharedProject(token: string): Promise<ApiResponse<SharedProject>> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'
  const response = await fetch(`${apiUrl}/share/public/${token}`)
  return response.json()
}

/**
 * Generate shareable URL
 */
export function getShareUrl(token: string): string {
  if (typeof window !== 'undefined') {
    return `${window.location.origin}/shared/${token}`
  }
  return `/shared/${token}`
}
