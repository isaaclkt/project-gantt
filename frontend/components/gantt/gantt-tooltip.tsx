'use client'

import { Task, TeamMember } from '@/lib/types'
import { formatDate, getStatusLabel, getStatusColor } from '@/lib/gantt-utils'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { CalendarDays, User } from 'lucide-react'

interface GanttTooltipProps {
  task: Task
  assignee?: TeamMember
  x: number
  y: number
}

/**
 * Gantt Tooltip Component
 * 
 * Shows detailed task information on hover.
 */
export function GanttTooltip({ task, assignee, x, y }: GanttTooltipProps) {
  return (
    <div
      className="absolute z-50 pointer-events-none"
      style={{
        left: x + 16,
        top: y - 10,
        transform: 'translateY(-50%)'
      }}
    >
      <div className="bg-popover border border-border rounded-lg shadow-lg p-3 min-w-[220px]">
        {/* Task Name */}
        <div className="flex items-start gap-2 mb-3">
          <div className={cn('w-2 h-2 rounded-full mt-1.5 shrink-0', getStatusColor(task.status))} />
          <div>
            <h4 className="font-medium text-sm text-popover-foreground">{task.name}</h4>
            <p className="text-xs text-muted-foreground line-clamp-2">{task.description}</p>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2">
          {/* Status */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Status</span>
            <span className={cn('font-medium', getStatusColor(task.status).replace('bg-', 'text-'))}>
              {getStatusLabel(task.status)}
            </span>
          </div>

          {/* Dates */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground flex items-center gap-1">
              <CalendarDays className="h-3 w-3" />
              Dates
            </span>
            <span className="text-popover-foreground">
              {formatDate(task.startDate)} - {formatDate(task.endDate)}
            </span>
          </div>

          {/* Progress */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Progress</span>
            <span className="text-popover-foreground">{task.progress}%</span>
          </div>

          {/* Assignee */}
          {assignee && (
            <div className="flex items-center justify-between text-xs pt-2 border-t border-border">
              <span className="text-muted-foreground flex items-center gap-1">
                <User className="h-3 w-3" />
                Assignee
              </span>
              <div className="flex items-center gap-2">
                <Avatar className="h-5 w-5">
                  <AvatarImage src={assignee.avatar || "/placeholder.svg"} />
                  <AvatarFallback className="text-[8px]">
                    {assignee.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')}
                  </AvatarFallback>
                </Avatar>
                <span className="text-popover-foreground">{assignee.name}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
