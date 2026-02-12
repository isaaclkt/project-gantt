'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Task, TeamMember, Project, CreateTaskInput, UpdateTaskInput } from '@/lib/types'
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  getTeamMembers,
  getProjects,
  getInsights
} from '@/lib/services'
import type { Insight } from '@/lib/services/insights-service'
import { DashboardLayout } from '@/components/layout'
import { GanttChart } from '@/components/gantt'
import { TaskFormDialog, TaskDetailDialog } from '@/components/tasks'
import { StatsCards, InsightsPanel } from '@/components/dashboard'
import { Loader2 } from 'lucide-react'
import { useAuth } from '@/contexts/auth-context'
import { useSettings } from '@/contexts/settings-context'
import { canCreateTask, canEditTask, canDeleteTask } from '@/lib/permissions'
import { ApiError, ERROR_CODES } from '@/lib/api-config'
import { useToast } from '@/components/ui/toast'
import { LandingPage } from '@/components/landing'

/**
 * Main Dashboard Page
 *
 * Central hub for project management with Gantt chart visualization.
 * Protected route - requires authentication.
 */
export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const { settings } = useSettings()
  const { toast } = useToast()
  const defaultView = settings?.displayPreferences?.defaultView ?? 'gantt'
  const router = useRouter()
  const userRole = user?.role
  const dataLoadedRef = useRef(false)

  // No redirect — show landing page for unauthenticated users

  // Data state
  const [tasks, setTasks] = useState<Task[]>([])
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [insights, setInsights] = useState<Insight[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Dialog state
  const [isFormDialogOpen, setIsFormDialogOpen] = useState(false)
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)

  // Only load data once when authenticated
  useEffect(() => {
    if (isAuthenticated && !dataLoadedRef.current) {
      dataLoadedRef.current = true

      const loadData = async () => {
        setIsLoading(true)
        try {
          const [tasksResponse, teamResponse, projectsResponse, insightsResponse] = await Promise.all([
            getTasks(),
            getTeamMembers(),
            getProjects(),
            getInsights()
          ])

          if (tasksResponse.success) setTasks(tasksResponse.data)
          if (teamResponse.success) setTeamMembers(teamResponse.data)
          if (projectsResponse.success) setProjects(projectsResponse.data)
          if (insightsResponse.success) setInsights(insightsResponse.data.insights)
        } catch (error) {
          if (error instanceof ApiError && error.code === ERROR_CODES.UNAUTHORIZED) {
            router.push('/login')
          }
        } finally {
          setIsLoading(false)
        }
      }

      loadData()
    }
  }, [isAuthenticated, router])

  // Open form dialog for new task
  const handleNewTask = () => {
    setSelectedTask(null)
    setIsFormDialogOpen(true)
  }

  // Open detail dialog for viewing task
  const handleTaskClick = (task: Task) => {
    setSelectedTask(task)
    setIsDetailDialogOpen(true)
  }

  // Open form dialog for editing task
  const handleTaskEdit = (task: Task) => {
    setSelectedTask(task)
    setIsDetailDialogOpen(false)
    setIsFormDialogOpen(true)
  }

  // Handle form submission (create or update)
  const handleFormSubmit = async (data: CreateTaskInput | UpdateTaskInput) => {
    try {
      if ('id' in data) {
        const response = await updateTask(data)
        if (response.success) {
          setTasks((prev) => prev.map((t) => (t.id === data.id ? response.data : t)))
          toast({ title: 'Tarefa atualizada', description: 'As alterações foram salvas.' })
        }
      } else {
        const response = await createTask(data)
        if (response.success) {
          setTasks((prev) => [...prev, response.data])
          toast({ title: 'Tarefa criada', description: 'A tarefa foi adicionada com sucesso.' })
        }
      }
    } catch {
      toast({ title: 'Erro', description: 'Não foi possível salvar a tarefa.', variant: 'destructive' })
    }
  }

  // Handle task deletion
  const handleTaskDelete = async (id: string) => {
    try {
      const response = await deleteTask(id)
      if (response.success) {
        setTasks((prev) => prev.filter((t) => t.id !== id))
        toast({ title: 'Tarefa excluída', description: 'A tarefa foi removida.' })
      }
    } catch {
      toast({ title: 'Erro ao excluir', description: 'Não foi possível excluir a tarefa.', variant: 'destructive' })
    }
  }

  // Handlers memoizados para evitar re-renders
  const handleFormDialogOpenChange = useCallback((open: boolean) => {
    setIsFormDialogOpen(open)
    if (!open) setSelectedTask(null)
  }, [])

  const handleDetailDialogOpenChange = useCallback((open: boolean) => {
    setIsDetailDialogOpen(open)
  }, [])

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    )
  }

  // Show landing page if not authenticated
  if (!isAuthenticated) {
    return <LandingPage />
  }

  // Loading state
  if (isLoading) {
    return (
      <DashboardLayout onNewTask={userRole && canCreateTask(userRole) ? handleNewTask : undefined}>
        <div className="h-full flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Carregando dados do projeto...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout onNewTask={userRole && canCreateTask(userRole) ? handleNewTask : undefined}>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-foreground">Painel de Projetos</h1>
          <p className="text-muted-foreground mt-1">
            Gerencie seus projetos e acompanhe o progresso no gráfico Gantt
          </p>
        </div>

        {/* Stats Cards */}
        <StatsCards tasks={tasks} />

        {/* Insights Panel */}
        <InsightsPanel insights={insights} />

        {/* Gantt Chart */}
        <GanttChart
          tasks={tasks}
          teamMembers={teamMembers}
          onTaskClick={handleTaskClick}
          onTaskEdit={handleTaskEdit}
        />
      </div>

      {/* Task Detail Dialog - Renderização condicional */}
      {isDetailDialogOpen && (
        <TaskDetailDialog
          open={isDetailDialogOpen}
          onOpenChange={handleDetailDialogOpenChange}
          task={selectedTask}
          teamMembers={teamMembers}
          projects={projects}
          onEdit={userRole && canEditTask(userRole) ? handleTaskEdit : undefined}
        />
      )}

      {/* Task Form Dialog - Renderização condicional */}
      {isFormDialogOpen && (
        <TaskFormDialog
          open={isFormDialogOpen}
          onOpenChange={handleFormDialogOpenChange}
          task={selectedTask}
          teamMembers={teamMembers}
          projects={projects}
          onSubmit={handleFormSubmit}
          onDelete={userRole && canDeleteTask(userRole) ? handleTaskDelete : undefined}
        />
      )}
    </DashboardLayout>
  )
}
