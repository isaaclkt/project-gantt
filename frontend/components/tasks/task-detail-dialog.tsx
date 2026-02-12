'use client'

import { Task, TeamMember, Project } from '@/lib/types'
import { formatDate, getStatusLabel, getStatusColor } from '@/lib/gantt-utils'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  CalendarDays,
  User,
  FolderKanban,
  Flag,
  Edit,
  Clock
} from 'lucide-react'

interface TaskDetailDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  task: Task | null
  teamMembers: TeamMember[]
  projects: Project[]
  onEdit?: (task: Task) => void
}

/**
 * Task Detail Dialog Component
 * 
 * Read-only view of task details with edit button.
 */
export function TaskDetailDialog({
  open,
  onOpenChange,
  task,
  teamMembers,
  projects,
  onEdit
}: TaskDetailDialogProps) {
  if (!task) return null

  const assignee = teamMembers.find((m) => m.id === task.assigneeId)
  const project = projects.find((p) => p.id === task.projectId)

  const priorityColors = {
    low: 'text-muted-foreground',
    medium: 'text-status-in-progress',
    high: 'text-destructive'
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className={cn('w-3 h-3 rounded-full mt-1.5 shrink-0', getStatusColor(task.status))} />
              <div>
                <DialogTitle className="text-xl">{task.name}</DialogTitle>
                <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Status */}
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Status
            </span>
            <span className={cn('text-sm font-medium px-2 py-1 rounded', getStatusColor(task.status), 'text-foreground')}>
              {getStatusLabel(task.status)}
            </span>
          </div>

          {/* Progress */}
          <div className="py-2 border-b border-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Progresso</span>
              <span className="text-sm font-medium">{task.progress}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={cn('h-full rounded-full transition-all', getStatusColor(task.status))}
                style={{ width: `${task.progress}%` }}
              />
            </div>
          </div>

          {/* Dates */}
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <CalendarDays className="h-4 w-4" />
              Período
            </span>
            <span className="text-sm">
              {formatDate(task.startDate)} - {formatDate(task.endDate)}
            </span>
          </div>

          {/* Project */}
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <FolderKanban className="h-4 w-4" />
              Projeto
            </span>
            <div className="flex items-center gap-2">
              {project && (
                <>
                  <div className="w-3 h-3 rounded" style={{ backgroundColor: project.color }} />
                  <span className="text-sm">{project.name}</span>
                </>
              )}
            </div>
          </div>

          {/* Priority */}
          <div className="flex items-center justify-between py-2 border-b border-border">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <Flag className="h-4 w-4" />
              Prioridade
            </span>
            <span className={cn('text-sm font-medium capitalize', priorityColors[task.priority])}>
              {task.priority}
            </span>
          </div>

          {/* Assignee */}
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-muted-foreground flex items-center gap-2">
              <User className="h-4 w-4" />
              Responsável
            </span>
            {assignee && (
              <div className="flex items-center gap-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={assignee.avatar || "/placeholder.svg"} />
                  <AvatarFallback className="text-xs">
                    {assignee.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm">{assignee.name}</span>
              </div>
            )}
          </div>
        </div>

        {onEdit && (
          <div className="flex justify-end">
            <Button onClick={() => onEdit(task)} className="gap-2">
              <Edit className="h-4 w-4" />
              Editar Tarefa
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
