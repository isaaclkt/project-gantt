# Project Grantt - API Documentation

## Base URL
```
http://localhost:5000/api
```

## Response Format

All API responses follow this structure:

```typescript
// Success response
interface ApiResponse<T> {
  data: T;
  success: true;
  message?: string;
}

// Paginated response
interface PaginatedResponse<T> {
  data: T;
  success: true;
  message?: string;
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Error response
interface ErrorResponse {
  data: null;
  success: false;
  message: string;
  errors?: object;
}
```

---

## Projects API

### GET /api/projects
Get all projects with optional filtering and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| status | string | - | Filter by status (planning, active, on-hold, completed) |
| page | number | 1 | Page number |
| limit | number | 10 | Items per page (max: 100) |

**Response:** `PaginatedResponse<Project[]>`

---

### GET /api/projects/:id
Get a single project by ID.

**Response:** `ApiResponse<Project>`

---

### POST /api/projects
Create a new project.

**Body:**
```json
{
  "name": "string (required)",
  "description": "string",
  "color": "string (hex color, e.g. #3B82F6)",
  "status": "planning | active | on-hold | completed",
  "startDate": "YYYY-MM-DD (required)",
  "endDate": "YYYY-MM-DD (required)",
  "teamMemberIds": ["string"]
}
```

**Response:** `ApiResponse<Project>` (201 Created)

---

### PUT /api/projects/:id
Update an existing project.

**Body:**
```json
{
  "name": "string",
  "description": "string",
  "color": "string",
  "status": "string",
  "progress": "number (0-100)",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "teamMemberIds": ["string"]
}
```

**Response:** `ApiResponse<Project>`

---

### DELETE /api/projects/:id
Delete a project.

**Response:** `ApiResponse<null>`

---

### GET /api/projects/:id/tasks
Get all tasks for a specific project.

**Response:** `ApiResponse<Task[]>`

---

### GET /api/projects/:id/members
Get all team members of a project.

**Response:** `ApiResponse<TeamMember[]>`

---

### POST /api/projects/:projectId/members/:teamMemberId
Add a team member to a project.

**Response:** `ApiResponse<Project>`

---

### DELETE /api/projects/:projectId/members/:teamMemberId
Remove a team member from a project.

**Response:** `ApiResponse<Project>`

---

## Tasks API

### GET /api/tasks
Get all tasks with optional filtering and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| projectId | string | - | Filter by project |
| status | string | - | Filter by status (todo, in-progress, review, completed) |
| assigneeId | string | - | Filter by assignee |
| priority | string | - | Filter by priority (low, medium, high) |
| page | number | 1 | Page number |
| limit | number | 50 | Items per page (max: 100) |

**Response:** `PaginatedResponse<Task[]>`

---

### GET /api/tasks/:id
Get a single task by ID.

**Response:** `ApiResponse<Task>` (includes assignee and project details)

---

### POST /api/tasks
Create a new task.

**Body:**
```json
{
  "name": "string (required)",
  "description": "string",
  "startDate": "YYYY-MM-DD (required)",
  "endDate": "YYYY-MM-DD (required)",
  "status": "todo | in-progress | review | completed",
  "priority": "low | medium | high",
  "assigneeId": "string",
  "projectId": "string (required)"
}
```

**Response:** `ApiResponse<Task>` (201 Created)

---

### PUT /api/tasks/:id
### PATCH /api/tasks/:id
Update an existing task.

**Body:**
```json
{
  "name": "string",
  "description": "string",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "status": "string",
  "priority": "string",
  "progress": "number (0-100)",
  "assigneeId": "string | null",
  "projectId": "string"
}
```

**Response:** `ApiResponse<Task>`

---

### DELETE /api/tasks/:id
Delete a task.

**Response:** `ApiResponse<null>`

---

### PATCH /api/tasks/:id/status
Quick update task status.

**Body:**
```json
{
  "status": "todo | in-progress | review | completed"
}
```

**Response:** `ApiResponse<Task>`

---

### PATCH /api/tasks/:id/progress
Quick update task progress.

**Body:**
```json
{
  "progress": "number (0-100)"
}
```

**Response:** `ApiResponse<Task>`

---

## Team API

### GET /api/team
Get all team members with optional filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| department | string | - | Filter by department |
| status | string | - | Filter by status (active, away, offline) |
| page | number | 1 | Page number |
| limit | number | 50 | Items per page (max: 100) |

**Response:** `PaginatedResponse<TeamMember[]>`

---

### GET /api/team/:id
Get a single team member by ID.

**Response:** `ApiResponse<TeamMember>`

---

### POST /api/team
Create a new team member.

**Body:**
```json
{
  "name": "string (required)",
  "email": "string (required)",
  "role": "string (required)",
  "department": "string",
  "status": "active | away | offline"
}
```

**Response:** `ApiResponse<TeamMember>` (201 Created)

---

### PUT /api/team/:id
Update an existing team member.

**Body:**
```json
{
  "name": "string",
  "email": "string",
  "role": "string",
  "department": "string",
  "status": "string"
}
```

**Response:** `ApiResponse<TeamMember>`

---

### DELETE /api/team/:id
Delete a team member.

**Response:** `ApiResponse<null>`

---

### GET /api/team/departments
Get list of all departments.

**Response:** `ApiResponse<string[]>`

---

## User API

### GET /api/users
Get all users (admin).

**Response:** `PaginatedResponse<User[]>`

---

### POST /api/users
Create a new user.

**Body:**
```json
{
  "name": "string (required)",
  "email": "string (required)",
  "password": "string (required)",
  "role": "string",
  "department": "string",
  "phone": "string",
  "timezone": "string"
}
```

**Response:** `ApiResponse<User>` (201 Created)

---

### GET /api/user/profile
Get current user's profile.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| userId | string | User ID (temporary, will use JWT) |

**Response:** `ApiResponse<UserProfile>`

---

### PUT /api/user/profile
Update current user's profile.

**Body:**
```json
{
  "name": "string",
  "email": "string",
  "phone": "string",
  "department": "string",
  "timezone": "string"
}
```

**Response:** `ApiResponse<UserProfile>`

---

### GET /api/user/settings
Get current user's settings.

**Response:** `ApiResponse<UserSettings>`

---

### PUT /api/user/settings
Update current user's settings.

**Body:**
```json
{
  "theme": "light | dark | system",
  "language": "string",
  "notifications": {
    "email": "boolean",
    "push": "boolean",
    "taskReminders": "boolean",
    "projectUpdates": "boolean"
  },
  "displayPreferences": {
    "compactMode": "boolean",
    "showAvatars": "boolean",
    "defaultView": "gantt | list | board"
  }
}
```

**Response:** `ApiResponse<UserSettings>`

---

## Authentication API (Prepared)

### POST /api/auth/login
Authenticate user.

**Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "data": {
    "accessToken": "string",
    "refreshToken": "string",
    "user": "User"
  },
  "success": true,
  "message": "Login successful"
}
```

---

### POST /api/auth/register
Register new user.

**Body:**
```json
{
  "name": "string (required)",
  "email": "string (required)",
  "password": "string (required, min 8 chars)",
  "role": "string",
  "department": "string"
}
```

**Response:** Same as login (201 Created)

---

### POST /api/auth/refresh
Refresh access token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "data": {
    "accessToken": "string"
  },
  "success": true
}
```

---

### POST /api/auth/logout
Logout user.

**Response:** `ApiResponse<null>`

---

### GET /api/auth/me
Get current authenticated user.

**Response:** `ApiResponse<User>`

---

### POST /api/auth/change-password
Change user password.

**Body:**
```json
{
  "currentPassword": "string (required)",
  "newPassword": "string (required, min 8 chars)"
}
```

**Response:** `ApiResponse<null>`

---

## Data Types

### Project
```typescript
interface Project {
  id: string;
  name: string;
  description: string;
  color: string;
  status: 'planning' | 'active' | 'on-hold' | 'completed';
  progress: number;
  startDate: string; // ISO date
  endDate: string; // ISO date
  teamMemberIds: string[];
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
}
```

### Task
```typescript
interface Task {
  id: string;
  name: string;
  description: string;
  startDate: string;
  endDate: string;
  status: 'todo' | 'in-progress' | 'review' | 'completed';
  priority: 'low' | 'medium' | 'high';
  progress: number;
  assigneeId: string | null;
  projectId: string;
  createdAt: string;
  updatedAt: string;
}
```

### TeamMember
```typescript
interface TeamMember {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: string;
  department: string | null;
  status: 'active' | 'away' | 'offline';
  joinedAt: string;
  createdAt: string;
  updatedAt: string;
}
```

### User
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: string;
  department: string | null;
  phone: string | null;
  timezone: string;
  status: 'active' | 'away' | 'offline';
  joinedAt: string;
  createdAt: string;
  updatedAt: string;
}
```

### UserSettings
```typescript
interface UserSettings {
  id: string;
  userId: string;
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    taskReminders: boolean;
    projectUpdates: boolean;
  };
  displayPreferences: {
    compactMode: boolean;
    showAvatars: boolean;
    defaultView: 'gantt' | 'list' | 'board';
  };
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists (e.g., duplicate email) |
| 500 | Internal Server Error |
