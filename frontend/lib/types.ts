// Task status types
export type TaskStatus = 'todo' | 'in-progress' | 'review' | 'completed'

// Gantt chart view mode
export type GanttViewMode = 'day' | 'week' | 'month'

// Team member status
export type MemberStatus = 'active' | 'away' | 'offline'

// Team member interface
export interface TeamMember {
  id: string
  name: string
  avatar: string
  email: string
  role: string
  status: MemberStatus
  department?: string
  joinedAt: string
}

// Task interface
export interface Task {
  id: string
  name: string
  description: string
  startDate: string // ISO date string
  endDate: string // ISO date string
  status: TaskStatus
  assigneeId: string
  projectId: string
  progress: number // 0-100
  priority: 'low' | 'medium' | 'high'
  createdAt: string
  updatedAt: string
}

// Project status type
export type ProjectStatus = 'planning' | 'active' | 'on-hold' | 'completed'

// Project interface
export interface Project {
  id: string
  name: string
  description: string
  color: string
  status: ProjectStatus
  progress: number // 0-100
  startDate: string
  endDate: string
  teamMemberIds: string[]
  createdAt: string
  updatedAt: string
}

// User settings interface
export interface UserSettings {
  id: string
  userId: string
  theme: 'light' | 'dark' | 'system'
  language: string
  notifications: {
    email: boolean
    push: boolean
    taskReminders: boolean
    projectUpdates: boolean
  }
  displayPreferences: {
    compactMode: boolean
    showAvatars: boolean
    defaultView: 'gantt' | 'list' | 'board'
  }
}

// User profile interface
export interface UserProfile {
  id: string
  name: string
  email: string
  avatar: string
  role: string
  department: string
  phone?: string
  timezone: string
  joinedAt: string
}

// API Response types - prepared for future backend integration
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Form types for CRUD operations
export interface CreateTaskInput {
  name: string
  description: string
  startDate: string
  endDate: string
  status: TaskStatus
  assigneeId: string
  projectId: string
  priority: 'low' | 'medium' | 'high'
}

export interface UpdateTaskInput extends Partial<CreateTaskInput> {
  id: string
  progress?: number
}

// Project form types
export interface CreateProjectInput {
  name: string
  description: string
  color: string
  status: ProjectStatus
  startDate: string
  endDate: string
  teamMemberIds: string[]
}

export interface UpdateProjectInput extends Partial<CreateProjectInput> {
  id: string
  progress?: number
}

// Team member form types
export interface CreateTeamMemberInput {
  name: string
  email: string
  role: string
  department?: string
  status: MemberStatus
}

export interface UpdateTeamMemberInput extends Partial<CreateTeamMemberInput> {
  id: string
}
