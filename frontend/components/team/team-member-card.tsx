'use client'

import { TeamMember } from '@/lib/types'
import { Card, CardContent } from '@/components/ui/card'
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
import { MoreHorizontal, Pencil, Trash2, Mail } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TeamMemberCardProps {
  member: TeamMember
  onEdit?: (member: TeamMember) => void
  onDelete?: (member: TeamMember) => void
  showAvatars?: boolean
}

const statusConfig: Record<TeamMember['status'], { label: string; className: string; dotClass: string }> = {
  active: {
    label: 'Ativo',
    className: 'bg-status-completed/20 text-status-completed border-status-completed/30',
    dotClass: 'bg-status-completed'
  },
  away: {
    label: 'Ausente',
    className: 'bg-status-in-progress/20 text-status-in-progress border-status-in-progress/30',
    dotClass: 'bg-status-in-progress'
  },
  offline: {
    label: 'Offline',
    className: 'bg-muted text-muted-foreground border-muted-foreground/30',
    dotClass: 'bg-muted-foreground'
  }
}

export function TeamMemberCard({ member, onEdit, onDelete, showAvatars = true }: TeamMemberCardProps) {
  const status = statusConfig[member.status]

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <Card className="group hover:border-primary/30 transition-colors">
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="relative">
            <Avatar className="h-16 w-16">
              {showAvatars && (
                <AvatarImage src={member.avatar || "/placeholder.svg"} alt={member.name} />
              )}
              <AvatarFallback className="text-lg">
                {member.name.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div
              className={cn(
                'absolute bottom-0 right-0 h-4 w-4 rounded-full border-2 border-card',
                status.dotClass
              )}
            />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-foreground">{member.name}</h3>
                <p className="text-sm text-muted-foreground">{member.role}</p>
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
                  {onEdit && (
                    <DropdownMenuItem onClick={() => onEdit(member)}>
                      <Pencil className="h-4 w-4 mr-2" />
                      Editar Membro
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={() => window.location.href = `mailto:${member.email}`}>
                    <Mail className="h-4 w-4 mr-2" />
                    Enviar E-mail
                  </DropdownMenuItem>
                  {onDelete && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        onClick={() => onDelete(member)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remover Membro
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <div className="mt-3 space-y-2">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <a
                  href={`mailto:${member.email}`}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors truncate"
                >
                  {member.email}
                </a>
              </div>
              {member.department && (
                <p className="text-sm text-muted-foreground">
                  {member.department}
                </p>
              )}
            </div>

            <div className="mt-4 flex items-center justify-between">
              <Badge variant="outline" className={cn('text-xs', status.className)}>
                {status.label}
              </Badge>
              <span className="text-xs text-muted-foreground">
                Desde {formatDate(member.joinedAt)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
