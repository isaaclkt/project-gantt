import { Task, TaskStatus, GanttViewMode } from './types'

/**
 * Gantt Chart Utility Functions
 * 
 * Helper functions for calculating positions, dates, and styling
 * for the Gantt chart visualization.
 */

// Get the number of days between two dates
export function getDaysBetween(start: Date, end: Date): number {
  const msPerDay = 1000 * 60 * 60 * 24
  return Math.ceil((end.getTime() - start.getTime()) / msPerDay)
}

// Get the start of the day
export function getStartOfDay(date: Date): Date {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

// Calculate the date range for a set of tasks
export function calculateDateRange(tasks: Task[]): { start: Date; end: Date; days: number } {
  if (tasks.length === 0) {
    const today = new Date()
    const start = getStartOfDay(today)
    const end = new Date(start)
    end.setDate(end.getDate() + 30)
    return { start, end, days: 30 }
  }

  const dates = tasks.flatMap((task) => [new Date(task.startDate), new Date(task.endDate)])

  let minDate = dates[0]
  let maxDate = dates[0]

  for (const date of dates) {
    if (date < minDate) minDate = date
    if (date > maxDate) maxDate = date
  }

  // Add padding days
  const start = getStartOfDay(minDate)
  start.setDate(start.getDate() - 3)

  const end = getStartOfDay(maxDate)
  end.setDate(end.getDate() + 5)

  const days = getDaysBetween(start, end)

  return { start, end, days: Math.max(days, 14) }
}

// Calculate the position and width of a task bar
export function calculateTaskBarPosition(
  task: Task,
  rangeStart: Date,
  totalDays: number
): { left: number; width: number } {
  const taskStart = getStartOfDay(new Date(task.startDate))
  const taskEnd = getStartOfDay(new Date(task.endDate))

  const startOffset = getDaysBetween(rangeStart, taskStart)
  const duration = getDaysBetween(taskStart, taskEnd) + 1

  const left = (startOffset / totalDays) * 100
  const width = (duration / totalDays) * 100

  return {
    left: Math.max(0, left),
    width: Math.min(width, 100 - left)
  }
}

// Get status color class
export function getStatusColor(status: TaskStatus): string {
  const colors: Record<TaskStatus, string> = {
    todo: 'bg-status-todo',
    'in-progress': 'bg-status-in-progress',
    review: 'bg-status-review',
    completed: 'bg-status-completed'
  }
  return colors[status]
}

// Get status label
export function getStatusLabel(status: TaskStatus): string {
  const labels: Record<TaskStatus, string> = {
    todo: 'A Fazer',
    'in-progress': 'Em Progresso',
    review: 'Em Revisão',
    completed: 'Concluída'
  }
  return labels[status]
}

// Format date for display
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('pt-BR', {
    month: 'short',
    day: 'numeric'
  })
}

// Format date for input fields
export function formatDateForInput(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toISOString().split('T')[0]
}

// Generate array of dates for timeline header
export function generateTimelineHeader(start: Date, days: number): Date[] {
  const dates: Date[] = []
  const current = new Date(start)

  for (let i = 0; i < days; i++) {
    dates.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }

  return dates
}

// Check if a date is today
export function isToday(date: Date): boolean {
  const today = new Date()
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  )
}

// Check if a date is weekend
export function isWeekend(date: Date): boolean {
  const day = date.getDay()
  return day === 0 || day === 6
}

// Get today's position in the timeline
export function getTodayPosition(rangeStart: Date, totalDays: number): number {
  const today = getStartOfDay(new Date())
  const offset = getDaysBetween(rangeStart, today)
  return (offset / totalDays) * 100
}

// ============================================
// Week/Month View Utilities
// ============================================

export interface TimelineItem {
  date: Date
  label: string
  subLabel?: string
  isCurrentPeriod: boolean
}

// Get the start of the week (Monday)
export function getStartOfWeek(date: Date): Date {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Adjust when day is Sunday
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

// Get the start of the month
export function getStartOfMonth(date: Date): Date {
  const d = new Date(date)
  d.setDate(1)
  d.setHours(0, 0, 0, 0)
  return d
}

// Get week number of the year
export function getWeekNumber(date: Date): number {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7)
}

// Check if date is in current week
export function isCurrentWeek(date: Date): boolean {
  const today = new Date()
  const weekStart = getStartOfWeek(today)
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekEnd.getDate() + 6)
  return date >= weekStart && date <= weekEnd
}

// Check if date is in current month
export function isCurrentMonth(date: Date): boolean {
  const today = new Date()
  return date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear()
}

// Generate timeline items for week view
export function generateWeekTimeline(start: Date, days: number): TimelineItem[] {
  const items: TimelineItem[] = []
  const current = getStartOfWeek(start)
  const endDate = new Date(start)
  endDate.setDate(endDate.getDate() + days)

  while (current <= endDate) {
    const weekNum = getWeekNumber(current)
    const monthName = current.toLocaleDateString('pt-BR', { month: 'short' })

    items.push({
      date: new Date(current),
      label: `Sem ${weekNum}`,
      subLabel: monthName,
      isCurrentPeriod: isCurrentWeek(current)
    })

    current.setDate(current.getDate() + 7)
  }

  return items
}

// Generate timeline items for month view
export function generateMonthTimeline(start: Date, days: number): TimelineItem[] {
  const items: TimelineItem[] = []
  const current = getStartOfMonth(start)
  const endDate = new Date(start)
  endDate.setDate(endDate.getDate() + days)

  while (current <= endDate) {
    const monthName = current.toLocaleDateString('pt-BR', { month: 'long' })
    const year = current.getFullYear()

    items.push({
      date: new Date(current),
      label: monthName.charAt(0).toUpperCase() + monthName.slice(1),
      subLabel: year.toString(),
      isCurrentPeriod: isCurrentMonth(current)
    })

    // Move to next month
    current.setMonth(current.getMonth() + 1)
  }

  return items
}

// Calculate the number of units (days, weeks, or months) in the range
export function calculateTimelineUnits(
  start: Date,
  days: number,
  viewMode: GanttViewMode
): number {
  if (viewMode === 'day') {
    return days
  }

  if (viewMode === 'week') {
    return Math.ceil(days / 7)
  }

  // Month view
  const endDate = new Date(start)
  endDate.setDate(endDate.getDate() + days)

  const startMonth = start.getFullYear() * 12 + start.getMonth()
  const endMonth = endDate.getFullYear() * 12 + endDate.getMonth()

  return endMonth - startMonth + 1
}

// Calculate task bar position based on view mode
export function calculateTaskBarPositionByViewMode(
  task: Task,
  rangeStart: Date,
  totalDays: number,
  viewMode: GanttViewMode
): { left: number; width: number } {
  const taskStart = getStartOfDay(new Date(task.startDate))
  const taskEnd = getStartOfDay(new Date(task.endDate))

  if (viewMode === 'day') {
    // Use original day-based calculation
    const startOffset = getDaysBetween(rangeStart, taskStart)
    const duration = getDaysBetween(taskStart, taskEnd) + 1

    const left = (startOffset / totalDays) * 100
    const width = (duration / totalDays) * 100

    return {
      left: Math.max(0, left),
      width: Math.min(width, 100 - Math.max(0, left))
    }
  }

  if (viewMode === 'week') {
    const weekStart = getStartOfWeek(rangeStart)
    const totalWeeks = Math.ceil(totalDays / 7)

    const startOffset = getDaysBetween(weekStart, taskStart) / 7
    const duration = (getDaysBetween(taskStart, taskEnd) + 1) / 7

    const left = (startOffset / totalWeeks) * 100
    const width = (duration / totalWeeks) * 100

    return {
      left: Math.max(0, left),
      width: Math.max(Math.min(width, 100 - Math.max(0, left)), 2) // Minimum 2% width
    }
  }

  // Month view
  const monthStart = getStartOfMonth(rangeStart)
  const endDate = new Date(rangeStart)
  endDate.setDate(endDate.getDate() + totalDays)

  const totalMonths = calculateTimelineUnits(rangeStart, totalDays, 'month')

  // Calculate offset in months
  const startMonthDiff = (taskStart.getFullYear() - monthStart.getFullYear()) * 12 +
                         (taskStart.getMonth() - monthStart.getMonth()) +
                         (taskStart.getDate() - 1) / 30 // Approximate day offset within month

  const endMonthDiff = (taskEnd.getFullYear() - monthStart.getFullYear()) * 12 +
                       (taskEnd.getMonth() - monthStart.getMonth()) +
                       taskEnd.getDate() / 30

  const left = (startMonthDiff / totalMonths) * 100
  const width = ((endMonthDiff - startMonthDiff) / totalMonths) * 100

  return {
    left: Math.max(0, left),
    width: Math.max(Math.min(width, 100 - Math.max(0, left)), 2) // Minimum 2% width
  }
}

// Get today's position based on view mode
export function getTodayPositionByViewMode(
  rangeStart: Date,
  totalDays: number,
  viewMode: GanttViewMode
): number {
  const today = getStartOfDay(new Date())

  if (viewMode === 'day') {
    const offset = getDaysBetween(rangeStart, today)
    return (offset / totalDays) * 100
  }

  if (viewMode === 'week') {
    const weekStart = getStartOfWeek(rangeStart)
    const totalWeeks = Math.ceil(totalDays / 7)
    const offset = getDaysBetween(weekStart, today) / 7
    return (offset / totalWeeks) * 100
  }

  // Month view
  const monthStart = getStartOfMonth(rangeStart)
  const totalMonths = calculateTimelineUnits(rangeStart, totalDays, 'month')

  const monthDiff = (today.getFullYear() - monthStart.getFullYear()) * 12 +
                    (today.getMonth() - monthStart.getMonth()) +
                    (today.getDate() - 1) / 30

  return (monthDiff / totalMonths) * 100
}
