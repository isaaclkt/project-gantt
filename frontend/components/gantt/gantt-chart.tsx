'use client'

import { useMemo, useRef, useState } from 'react'
import { Task, TeamMember, GanttViewMode } from '@/lib/types'
import {
  calculateDateRange,
  calculateTaskBarPositionByViewMode,
  getStatusColor,
  generateTimelineHeader,
  generateWeekTimeline,
  generateMonthTimeline,
  isToday,
  isWeekend,
  getTodayPositionByViewMode,
  TimelineItem
} from '@/lib/gantt-utils'
import { cn } from '@/lib/utils'
import { GanttTaskBar } from './gantt-task-bar'
import { GanttTooltip } from './gantt-tooltip'

interface GanttChartProps {
  tasks: Task[]
  teamMembers: TeamMember[]
  onTaskClick: (task: Task) => void
  onTaskEdit: (task: Task) => void
  defaultViewMode?: GanttViewMode
}

const viewModeLabels: Record<GanttViewMode, string> = {
  day: 'Dia',
  week: 'Semana',
  month: 'Mês',
}

/**
 * Gantt Chart Component
 *
 * Interactive Gantt chart visualization for project tasks.
 * Features:
 * - Timeline header with dates
 * - Task bars with status colors
 * - Today indicator line
 * - Hover tooltips
 * - Click to view/edit tasks
 * - View mode selector (Day / Week / Month)
 */
export function GanttChart({ tasks, teamMembers, onTaskClick, onTaskEdit, defaultViewMode = 'day' }: GanttChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoveredTask, setHoveredTask] = useState<Task | null>(null)
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 })
  const [viewMode, setViewMode] = useState<GanttViewMode>(defaultViewMode)

  // Calculate date range and timeline
  const { start: rangeStart, days: totalDays } = useMemo(() => calculateDateRange(tasks), [tasks])

  // Day view data (original behavior)
  const timelineDates = useMemo(() => generateTimelineHeader(rangeStart, totalDays), [rangeStart, totalDays])

  // Week/Month view data
  const weekTimeline = useMemo(() => generateWeekTimeline(rangeStart, totalDays), [rangeStart, totalDays])
  const monthTimeline = useMemo(() => generateMonthTimeline(rangeStart, totalDays), [rangeStart, totalDays])

  // Today position based on view mode
  const todayPosition = useMemo(
    () => getTodayPositionByViewMode(rangeStart, totalDays, viewMode),
    [rangeStart, totalDays, viewMode]
  )

  // Get team member by ID
  const getTeamMember = (id: string) => teamMembers.find((m) => m.id === id)

  // Handle mouse move for tooltip
  const handleMouseMove = (e: React.MouseEvent, task: Task) => {
    const container = containerRef.current
    if (!container) return

    const rect = container.getBoundingClientRect()
    setTooltipPosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    setHoveredTask(task)
  }

  // Cell width calculation based on view mode
  const cellWidth = useMemo(() => {
    if (viewMode === 'day') {
      return Math.max(40, 1200 / totalDays)
    }
    if (viewMode === 'week') {
      const totalWeeks = weekTimeline.length
      return Math.max(100, 1200 / totalWeeks)
    }
    // Month
    const totalMonths = monthTimeline.length
    return Math.max(140, 1200 / totalMonths)
  }, [viewMode, totalDays, weekTimeline.length, monthTimeline.length])

  // Total width based on view mode
  const totalWidth = useMemo(() => {
    if (viewMode === 'day') return cellWidth * totalDays
    if (viewMode === 'week') return cellWidth * weekTimeline.length
    return cellWidth * monthTimeline.length
  }, [viewMode, cellWidth, totalDays, weekTimeline.length, monthTimeline.length])

  // Get the current timeline items for week/month views
  const currentTimeline: TimelineItem[] = viewMode === 'week' ? weekTimeline : monthTimeline

  return (
    <div className="bg-card rounded-lg border border-border overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-lg font-semibold text-foreground">Project Timeline</h2>
        <div className="flex items-center gap-4">
          {/* View Mode Selector */}
          <div className="flex items-center rounded-md border border-border overflow-hidden">
            {(['day', 'week', 'month'] as GanttViewMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={cn(
                  'px-3 py-1.5 text-xs font-medium transition-colors',
                  viewMode === mode
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-muted-foreground hover:bg-muted/50'
                )}
              >
                {viewModeLabels[mode]}
              </button>
            ))}
          </div>

          {/* Status Legend */}
          <div className="hidden md:flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-status-todo" />
              <span className="text-muted-foreground">A Fazer</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-status-in-progress" />
              <span className="text-muted-foreground">Em Progresso</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-status-review" />
              <span className="text-muted-foreground">Revisão</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-status-completed" />
              <span className="text-muted-foreground">Concluída</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex" ref={containerRef}>
        {/* Task List (Left Panel) */}
        <div className="w-64 shrink-0 border-r border-border">
          {/* Header */}
          <div className="h-12 border-b border-border bg-muted/30 px-4 flex items-center">
            <span className="text-sm font-medium text-muted-foreground">Task Name</span>
          </div>

          {/* Task Rows */}
          <div>
            {tasks.map((task) => {
              const assignee = getTeamMember(task.assigneeId)
              return (
                <div
                  key={task.id}
                  className="h-14 border-b border-border px-4 flex items-center gap-3 hover:bg-muted/30 cursor-pointer transition-colors"
                  onClick={() => onTaskClick(task)}
                >
                  <div className={cn('w-2 h-2 rounded-full shrink-0', getStatusColor(task.status))} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{task.name}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {assignee?.name || 'Unassigned'}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Timeline (Right Panel) */}
        <div className="flex-1 overflow-x-auto">
          <div style={{ minWidth: totalWidth }}>
            {/* Timeline Header */}
            <div className="h-12 border-b border-border bg-muted/30 flex relative">
              {viewMode === 'day' ? (
                /* Day View Header (original) */
                timelineDates.map((date, index) => (
                  <div
                    key={index}
                    className={cn(
                      'shrink-0 flex items-center justify-center text-xs border-r border-border/50',
                      isToday(date) && 'bg-primary/10',
                      isWeekend(date) && 'bg-muted/50'
                    )}
                    style={{ width: cellWidth }}
                  >
                    <div className="text-center">
                      <div className={cn('font-medium', isToday(date) ? 'text-primary' : 'text-foreground')}>
                        {date.getDate()}
                      </div>
                      <div className="text-muted-foreground text-[10px]">
                        {date.toLocaleDateString('en-US', { weekday: 'short' })}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                /* Week / Month View Header */
                currentTimeline.map((item, index) => (
                  <div
                    key={index}
                    className={cn(
                      'shrink-0 flex items-center justify-center text-xs border-r border-border/50',
                      item.isCurrentPeriod && 'bg-primary/10'
                    )}
                    style={{ width: cellWidth }}
                  >
                    <div className="text-center">
                      <div className={cn(
                        'font-medium',
                        item.isCurrentPeriod ? 'text-primary' : 'text-foreground'
                      )}>
                        {item.label}
                      </div>
                      {item.subLabel && (
                        <div className="text-muted-foreground text-[10px]">
                          {item.subLabel}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Task Bars */}
            <div className="relative">
              {/* Grid Lines */}
              <div className="absolute inset-0 flex pointer-events-none">
                {viewMode === 'day' ? (
                  timelineDates.map((date, index) => (
                    <div
                      key={index}
                      className={cn(
                        'shrink-0 border-r border-border/30',
                        isWeekend(date) && 'bg-muted/20'
                      )}
                      style={{ width: cellWidth }}
                    />
                  ))
                ) : (
                  currentTimeline.map((item, index) => (
                    <div
                      key={index}
                      className={cn(
                        'shrink-0 border-r border-border/30',
                        item.isCurrentPeriod && 'bg-primary/5'
                      )}
                      style={{ width: cellWidth }}
                    />
                  ))
                )}
              </div>

              {/* Today Line */}
              {todayPosition >= 0 && todayPosition <= 100 && (
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-primary z-10"
                  style={{ left: `${todayPosition}%` }}
                />
              )}

              {/* Task Bars */}
              {tasks.map((task) => {
                const { left, width } = calculateTaskBarPositionByViewMode(
                  task, rangeStart, totalDays, viewMode
                )
                const assignee = getTeamMember(task.assigneeId)

                return (
                  <div key={task.id} className="h-14 border-b border-border relative">
                    <GanttTaskBar
                      task={task}
                      left={left}
                      width={width}
                      assignee={assignee}
                      onMouseMove={(e) => handleMouseMove(e, task)}
                      onMouseLeave={() => setHoveredTask(null)}
                      onClick={() => onTaskEdit(task)}
                    />
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Tooltip */}
      {hoveredTask && (
        <GanttTooltip
          task={hoveredTask}
          assignee={getTeamMember(hoveredTask.assigneeId)}
          x={tooltipPosition.x}
          y={tooltipPosition.y}
        />
      )}
    </div>
  )
}
