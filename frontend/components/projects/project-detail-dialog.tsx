'use client'

import { Project, TeamMember, Task } from '@/lib/types'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Calendar, Users, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ProjectDetailDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  project: Project | null
  teamMembers: TeamMember[]
  tasks: Task[]
}

const statusConfig: Record<Project['status'], { label: string; className: string }> = {
  planning: { label: 'Planejamento', className: 'bg-status-todo/20 text-status-todo border-status-todo/30' },
  active: { label: 'Ativo', className: 'bg-status-in-progress/20 text-status-in-progress border-status-in-progress/30' },
  'on-hold': { label: 'Pausado', className: 'bg-status-review/20 text-status-review border-status-review/30' },
  completed: { label: 'Concluído', className: 'bg-status-completed/20 text-status-completed border-status-completed/30' }
}

export function ProjectDetailDialog({
  open,
  onOpenChange,
  project,
  teamMembers,
  tasks
}: ProjectDetailDialogProps) {
  if (!project) return null

  const status = statusConfig[project.status]
  const projectMembers = teamMembers.filter(m => project.teamMemberIds.includes(m.id))
  const projectTasks = tasks.filter(t => t.projectId === project.id)

  const taskStats = {
    total: projectTasks.length,
    completed: projectTasks.filter(t => t.status === 'completed').length,
    inProgress: projectTasks.filter(t => t.status === 'in-progress').length,
    todo: projectTasks.filter(t => t.status === 'todo').length
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div
              className="h-4 w-4 rounded-full shrink-0"
              style={{ backgroundColor: project.color }}
            />
            <DialogTitle className="text-xl">{project.name}</DialogTitle>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Status and Progress */}
          <div className="flex items-center justify-between">
            <Badge variant="outline" className={cn('text-sm', status.className)}>
              {status.label}
            </Badge>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Progresso:</span>
              <span className="text-lg font-semibold text-foreground">{project.progress}%</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="h-3 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${project.progress}%` }}
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">Descrição</h4>
            <p className="text-foreground">{project.description}</p>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-secondary/30 rounded-lg space-y-1">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span className="text-sm">Data de Início</span>
              </div>
              <p className="font-medium text-foreground">{formatDate(project.startDate)}</p>
            </div>
            <div className="p-4 bg-secondary/30 rounded-lg space-y-1">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span className="text-sm">Data de Término</span>
              </div>
              <p className="font-medium text-foreground">{formatDate(project.endDate)}</p>
            </div>
          </div>

          {/* Task Stats */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Resumo de Tarefas
            </h4>
            <div className="grid grid-cols-4 gap-3">
              <div className="p-3 bg-secondary/30 rounded-lg text-center">
                <p className="text-2xl font-bold text-foreground">{taskStats.total}</p>
                <p className="text-xs text-muted-foreground">Total</p>
              </div>
              <div className="p-3 bg-status-completed/10 rounded-lg text-center">
                <p className="text-2xl font-bold text-status-completed">{taskStats.completed}</p>
                <p className="text-xs text-muted-foreground">Concluídas</p>
              </div>
              <div className="p-3 bg-status-in-progress/10 rounded-lg text-center">
                <p className="text-2xl font-bold text-status-in-progress">{taskStats.inProgress}</p>
                <p className="text-xs text-muted-foreground">Em Progresso</p>
              </div>
              <div className="p-3 bg-status-todo/10 rounded-lg text-center">
                <p className="text-2xl font-bold text-status-todo">{taskStats.todo}</p>
                <p className="text-xs text-muted-foreground">A Fazer</p>
              </div>
            </div>
          </div>

          {/* Team Members */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4" />
              Membros da Equipe ({projectMembers.length})
            </h4>
            <div className="grid gap-2">
              {projectMembers.map(member => (
                <div
                  key={member.id}
                  className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg"
                >
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={member.avatar || "/placeholder.svg"} alt={member.name} />
                    <AvatarFallback>
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-foreground">{member.name}</p>
                    <p className="text-sm text-muted-foreground">{member.role}</p>
                  </div>
                  <Badge
                    variant="outline"
                    className={cn(
                      'text-xs',
                      member.status === 'active' && 'bg-status-completed/20 text-status-completed',
                      member.status === 'away' && 'bg-status-in-progress/20 text-status-in-progress',
                      member.status === 'offline' && 'bg-muted text-muted-foreground'
                    )}
                  >
                    {member.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
