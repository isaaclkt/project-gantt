'use client'

import { Project, TeamMember } from '@/lib/types'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { MoreHorizontal, Eye, Pencil, Trash2, Calendar, Users, Share2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ProjectCardProps {
  project: Project
  teamMembers: TeamMember[]
  onView: (project: Project) => void
  onEdit?: (project: Project) => void
  onDelete?: (project: Project) => void
  onShare?: (project: Project) => void
}

const statusConfig: Record<Project['status'], { label: string; className: string }> = {
  planning: { label: 'Planejamento', className: 'bg-status-todo/20 text-status-todo border-status-todo/30' },
  active: { label: 'Ativo', className: 'bg-status-in-progress/20 text-status-in-progress border-status-in-progress/30' },
  'on-hold': { label: 'Pausado', className: 'bg-status-review/20 text-status-review border-status-review/30' },
  completed: { label: 'Concluído', className: 'bg-status-completed/20 text-status-completed border-status-completed/30' }
}

export function ProjectCard({ project, teamMembers, onView, onEdit, onDelete, onShare }: ProjectCardProps) {
  const status = statusConfig[project.status]
  const projectMembers = teamMembers.filter(m => project.teamMemberIds.includes(m.id))
  const displayedMembers = projectMembers.slice(0, 4)
  const remainingCount = projectMembers.length - 4

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  return (
    <Card className="group hover:border-primary/30 transition-colors">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className="h-3 w-3 rounded-full shrink-0"
              style={{ backgroundColor: project.color }}
            />
            <h3 className="font-semibold text-foreground leading-tight">{project.name}</h3>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onView(project)}>
                <Eye className="h-4 w-4 mr-2" />
                Ver Detalhes
              </DropdownMenuItem>
              {onShare && (
                <DropdownMenuItem onClick={() => onShare(project)}>
                  <Share2 className="h-4 w-4 mr-2" />
                  Compartilhar
                </DropdownMenuItem>
              )}
              {onEdit && (
                <DropdownMenuItem onClick={() => onEdit(project)}>
                  <Pencil className="h-4 w-4 mr-2" />
                  Editar Projeto
                </DropdownMenuItem>
              )}
              {onDelete && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => onDelete(project)}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Excluir Projeto
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <Badge variant="outline" className={cn('w-fit', status.className)}>
          {status.label}
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground line-clamp-2">{project.description}</p>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progresso</span>
            <span className="font-medium text-foreground">{project.progress}%</span>
          </div>
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${project.progress}%` }}
            />
          </div>
        </div>

        {/* Dates */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Calendar className="h-4 w-4" />
            <span>{formatDate(project.startDate)}</span>
          </div>
          <span>-</span>
          <span>{formatDate(project.endDate)}</span>
        </div>

        {/* Team Members */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            <span>{projectMembers.length} membros</span>
          </div>
          <div className="flex -space-x-2">
            {displayedMembers.map(member => (
              <Avatar key={member.id} className="h-7 w-7 border-2 border-card">
                <AvatarImage src={member.avatar || "/placeholder.svg"} alt={member.name} />
                <AvatarFallback className="text-xs">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
            ))}
            {remainingCount > 0 && (
              <div className="h-7 w-7 rounded-full bg-secondary border-2 border-card flex items-center justify-center">
                <span className="text-xs font-medium text-secondary-foreground">+{remainingCount}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
