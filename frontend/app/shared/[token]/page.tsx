'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getSharedProject, SharedProject } from '@/lib/services/share-service'
import { GanttChart } from '@/components/gantt'
import { Task, TeamMember } from '@/lib/types'
import { Loader2, AlertCircle, Calendar, Users, CheckCircle2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

export default function SharedProjectPage() {
  const params = useParams()
  const token = params.token as string

  const [project, setProject] = useState<SharedProject | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadProject() {
      try {
        const response = await getSharedProject(token)
        if (response.success && response.data) {
          setProject(response.data)
        } else {
          setError(response.message || 'Link inválido ou expirado')
        }
      } catch {
        setError('Não foi possível carregar o projeto')
      } finally {
        setIsLoading(false)
      }
    }
    loadProject()
  }, [token])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Carregando projeto...</p>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md">
          <AlertCircle className="h-16 w-16 text-destructive mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Link Inválido</h1>
          <p className="text-muted-foreground">{error || 'Este link de compartilhamento não existe ou expirou.'}</p>
        </div>
      </div>
    )
  }

  // Convert project tasks to the format expected by GanttChart
  const tasks: Task[] = project.tasks.map(task => ({
    id: task.id,
    name: task.name,
    description: task.description,
    startDate: task.startDate,
    endDate: task.endDate,
    status: task.status as Task['status'],
    priority: task.priority as Task['priority'],
    progress: task.progress,
    assigneeId: task.assigneeId || '',
    projectId: project.id,
    createdAt: '',
    updatedAt: ''
  }))

  // Convert team members
  const teamMembers: TeamMember[] = project.teamMembers.map(member => ({
    id: member.id,
    name: member.name,
    avatar: member.avatar,
    email: '',
    role: member.role,
    status: 'active' as const,
    department: '',
    joinedAt: ''
  }))

  const completedTasks = tasks.filter(t => t.status === 'completed').length

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: project.color }}
                />
                <h1 className="text-2xl font-bold">{project.name}</h1>
              </div>
              {project.description && (
                <p className="text-muted-foreground">{project.description}</p>
              )}
            </div>
            <div className="text-sm text-muted-foreground bg-secondary px-3 py-1 rounded">
              Visualização compartilhada
            </div>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <Calendar className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Período</p>
                <p className="font-medium">
                  {new Date(project.startDate).toLocaleDateString('pt-BR')} - {new Date(project.endDate).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <CheckCircle2 className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Progresso</p>
                <p className="font-medium">{completedTasks} de {tasks.length} tarefas concluídas</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <Users className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Equipe</p>
                <p className="font-medium">{teamMembers.length} membro{teamMembers.length !== 1 ? 's' : ''}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Gantt Chart */}
        <Card>
          <CardContent className="p-4">
            <GanttChart
              tasks={tasks}
              teamMembers={teamMembers}
              onTaskClick={() => {}}
              onTaskEdit={() => {}}
            />
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground mt-8">
          Visualização gerada por ProjectFlow
        </div>
      </div>
    </div>
  )
}
