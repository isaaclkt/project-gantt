# Frontend Integration Guide

This document shows how to update the frontend services to connect to the real Flask backend API.

## Configuration

Create a configuration file for the API base URL:

```typescript
// frontend/lib/config.ts
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
```

Add to your `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

---

## Updated Service Examples

### Project Service

Replace `frontend/lib/services/project-service.ts`:

```typescript
import { API_BASE_URL } from '../config';
import type { Project, CreateProjectInput, UpdateProjectInput, ApiResponse, PaginatedResponse } from '../types';

export const projectService = {
  async getProjects(params?: { status?: string; page?: number; limit?: number }): Promise<PaginatedResponse<Project[]>> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/projects?${searchParams}`);
    return response.json();
  },

  async getProjectById(id: string): Promise<ApiResponse<Project>> {
    const response = await fetch(`${API_BASE_URL}/projects/${id}`);
    return response.json();
  },

  async createProject(input: CreateProjectInput): Promise<ApiResponse<Project>> {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return response.json();
  },

  async updateProject(input: UpdateProjectInput): Promise<ApiResponse<Project>> {
    const { id, ...data } = input;
    const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async deleteProject(id: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${API_BASE_URL}/projects/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  },

  async getProjectTasks(projectId: string): Promise<ApiResponse<Task[]>> {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/tasks`);
    return response.json();
  },
};
```

---

### Task Service

Replace `frontend/lib/services/task-service.ts`:

```typescript
import { API_BASE_URL } from '../config';
import type { Task, CreateTaskInput, UpdateTaskInput, ApiResponse, PaginatedResponse } from '../types';

export const taskService = {
  async getTasks(params?: {
    projectId?: string;
    status?: string;
    assigneeId?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Task[]>> {
    const searchParams = new URLSearchParams();
    if (params?.projectId) searchParams.set('projectId', params.projectId);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.assigneeId) searchParams.set('assigneeId', params.assigneeId);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/tasks?${searchParams}`);
    return response.json();
  },

  async getTaskById(id: string): Promise<ApiResponse<Task>> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`);
    return response.json();
  },

  async getTasksByProject(projectId: string): Promise<ApiResponse<Task[]>> {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/tasks`);
    return response.json();
  },

  async createTask(input: CreateTaskInput): Promise<ApiResponse<Task>> {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return response.json();
  },

  async updateTask(input: UpdateTaskInput): Promise<ApiResponse<Task>> {
    const { id, ...data } = input;
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async deleteTask(id: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  },

  async updateTaskStatus(id: string, status: Task['status']): Promise<ApiResponse<Task>> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    return response.json();
  },

  async updateTaskProgress(id: string, progress: number): Promise<ApiResponse<Task>> {
    const response = await fetch(`${API_BASE_URL}/tasks/${id}/progress`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ progress }),
    });
    return response.json();
  },
};
```

---

### Team Service

Replace `frontend/lib/services/team-service.ts`:

```typescript
import { API_BASE_URL } from '../config';
import type { TeamMember, CreateTeamMemberInput, UpdateTeamMemberInput, ApiResponse, PaginatedResponse } from '../types';

export const teamService = {
  async getTeamMembers(params?: {
    department?: string;
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<PaginatedResponse<TeamMember[]>> {
    const searchParams = new URLSearchParams();
    if (params?.department) searchParams.set('department', params.department);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/team?${searchParams}`);
    return response.json();
  },

  async getTeamMemberById(id: string): Promise<ApiResponse<TeamMember>> {
    const response = await fetch(`${API_BASE_URL}/team/${id}`);
    return response.json();
  },

  async createTeamMember(input: CreateTeamMemberInput): Promise<ApiResponse<TeamMember>> {
    const response = await fetch(`${API_BASE_URL}/team`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return response.json();
  },

  async updateTeamMember(input: UpdateTeamMemberInput): Promise<ApiResponse<TeamMember>> {
    const { id, ...data } = input;
    const response = await fetch(`${API_BASE_URL}/team/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async deleteTeamMember(id: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${API_BASE_URL}/team/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  },

  async getDepartments(): Promise<ApiResponse<string[]>> {
    const response = await fetch(`${API_BASE_URL}/team/departments`);
    return response.json();
  },
};
```

---

### Settings Service

Replace `frontend/lib/services/settings-service.ts`:

```typescript
import { API_BASE_URL } from '../config';
import type { UserProfile, UserSettings, ApiResponse } from '../types';

export const settingsService = {
  async getUserProfile(): Promise<ApiResponse<UserProfile>> {
    const response = await fetch(`${API_BASE_URL}/user/profile`);
    return response.json();
  },

  async updateUserProfile(updates: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    const response = await fetch(`${API_BASE_URL}/user/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  },

  async getUserSettings(): Promise<ApiResponse<UserSettings>> {
    const response = await fetch(`${API_BASE_URL}/user/settings`);
    return response.json();
  },

  async updateUserSettings(updates: Partial<UserSettings>): Promise<ApiResponse<UserSettings>> {
    const response = await fetch(`${API_BASE_URL}/user/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  },
};
```

---

## SWR Fetcher Update

Update your SWR fetcher to work with the API:

```typescript
// frontend/lib/fetcher.ts
import { API_BASE_URL } from './config';

export const fetcher = async (url: string) => {
  const response = await fetch(`${API_BASE_URL}${url}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'An error occurred');
  }

  const data = await response.json();
  return data.data; // Extract data from ApiResponse wrapper
};
```

---

## Authentication Integration (When Ready)

When you implement authentication, add token handling:

```typescript
// frontend/lib/auth.ts
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const auth = {
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  },

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  clearTokens(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  async login(email: string, password: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.message);
    }

    this.setTokens(data.data.accessToken, data.data.refreshToken);
  },

  async logout(): Promise<void> {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
      },
    });
    this.clearTokens();
  },
};

// Add to fetcher for authenticated requests
export const authFetcher = async (url: string) => {
  const token = auth.getToken();

  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'An error occurred');
  }

  const data = await response.json();
  return data.data;
};
```

---

## Error Handling

Add a utility for handling API errors:

```typescript
// frontend/lib/api-error.ts
export class ApiError extends Error {
  status: number;
  errors?: object;

  constructor(message: string, status: number, errors?: object) {
    super(message);
    this.status = status;
    this.errors = errors;
  }
}

export const handleApiResponse = async <T>(response: Response): Promise<T> => {
  const data = await response.json();

  if (!response.ok || !data.success) {
    throw new ApiError(
      data.message || 'An error occurred',
      response.status,
      data.errors
    );
  }

  return data.data;
};
```

---

## Running Both Servers

### Development Setup

1. **Start the Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
flask init-db
flask seed-db  # Add sample data
python run.py
```

2. **Start the Frontend:**
```bash
cd frontend
npm install
npm run dev
```

The backend will run on `http://localhost:5000` and frontend on `http://localhost:3000`.

---

## CORS Note

The backend is configured to allow requests from `http://localhost:3000`. If you change the frontend port, update the `CORS_ORIGINS` environment variable in the backend.
