'use client'

import React from "react"

import { Task, TeamMember } from '@/lib/types'
import { getStatusColor } from '@/lib/gantt-utils'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

interface GanttTaskBarProps {
  task: Task
  left: number
  width: number
  assignee?: TeamMember
  onMouseMove: (e: React.MouseEvent) => void
  onMouseLeave: () => void
  onClick: () => void
}

/**
 * Gantt Task Bar Component
 * 
 * Individual task bar with progress indicator and assignee avatar.
 * Interactive with hover and click states.
 */
export function GanttTaskBar({
  task,
  left,
  width,
  assignee,
  onMouseMove,
  onMouseLeave,
  onClick
}: GanttTaskBarProps) {
  return (
    <div
      className={cn(
        'absolute top-2 h-10 rounded-md cursor-pointer transition-all',
        'hover:ring-2 hover:ring-ring hover:ring-offset-1 hover:ring-offset-background',
        getStatusColor(task.status)
      )}
      style={{
        left: `${left}%`,
        width: `${Math.max(width, 2)}%`
      }}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
    >
      {/* Progress Bar (for in-progress tasks) */}
      {task.progress > 0 && task.progress < 100 && (
        <div
          className="absolute inset-0 bg-foreground/20 rounded-md"
          style={{ width: `${task.progress}%` }}
        />
      )}

      {/* Content */}
      <div className="absolute inset-0 px-2 flex items-center gap-2 overflow-hidden">
        {/* Task Name */}
        <span className="text-xs font-medium text-foreground truncate flex-1">
          {width > 5 ? task.name : ''}
        </span>

        {/* Assignee Avatar (show only if enough space) */}
        {assignee && width > 8 && (
          <Avatar className="h-6 w-6 shrink-0 ring-2 ring-background">
            <AvatarImage src={assignee.avatar || "/placeholder.svg"} alt={assignee.name} />
            <AvatarFallback className="text-[10px]">
              {assignee.name
                .split(' ')
                .map((n) => n[0])
                .join('')}
            </AvatarFallback>
          </Avatar>
        )}
      </div>
    </div>
  )
}
