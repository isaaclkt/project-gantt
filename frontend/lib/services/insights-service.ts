/**
 * Insights Service Layer
 * Connected to Flask Backend API
 */

import { ApiResponse } from '../types'
import { apiFetch } from '../api-config'

export interface Insight {
  type: 'critical' | 'warning' | 'positive' | 'info'
  icon: string
  title: string
  description: string
}

export interface InsightsResponse {
  insights: Insight[]
  generatedAt: string
}

/**
 * Fetch smart insights from the backend
 */
export async function getInsights(): Promise<ApiResponse<InsightsResponse>> {
  const response = await apiFetch<ApiResponse<InsightsResponse>>('/insights')
  return response
}
