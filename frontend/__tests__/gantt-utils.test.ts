import {
  getDaysBetween,
  getStartOfDay,
  calculateDateRange,
  calculateTaskBarPosition,
  getStatusColor,
  getStatusLabel,
  formatDateForInput,
  generateTimelineHeader,
  isWeekend,
  getStartOfWeek,
  getStartOfMonth,
  getWeekNumber,
  calculateTimelineUnits,
  generateWeekTimeline,
  generateMonthTimeline,
} from '@/lib/gantt-utils'
import { Task } from '@/lib/types'

describe('gantt-utils', () => {
  describe('getDaysBetween', () => {
    it('returns correct number of days', () => {
      const start = new Date('2025-01-01')
      const end = new Date('2025-01-10')
      expect(getDaysBetween(start, end)).toBe(9)
    })

    it('returns 0 for same day', () => {
      const date = new Date('2025-01-01')
      expect(getDaysBetween(date, date)).toBe(0)
    })

    it('handles negative difference', () => {
      const start = new Date('2025-01-10')
      const end = new Date('2025-01-01')
      expect(getDaysBetween(start, end)).toBeLessThan(0)
    })
  })

  describe('getStartOfDay', () => {
    it('zeroes out time component', () => {
      const date = new Date('2025-06-15T14:30:45.123Z')
      const result = getStartOfDay(date)
      expect(result.getHours()).toBe(0)
      expect(result.getMinutes()).toBe(0)
      expect(result.getSeconds()).toBe(0)
      expect(result.getMilliseconds()).toBe(0)
    })

    it('does not mutate original date', () => {
      const date = new Date('2025-06-15T14:30:00Z')
      const original = date.getTime()
      getStartOfDay(date)
      expect(date.getTime()).toBe(original)
    })
  })

  describe('calculateDateRange', () => {
    it('returns default 30-day range for empty tasks', () => {
      const result = calculateDateRange([])
      expect(result.days).toBe(30)
    })

    it('calculates range with padding for tasks', () => {
      const tasks: Task[] = [
        {
          id: '1', name: 'Task 1', description: '',
          startDate: '2025-06-01', endDate: '2025-06-10',
          status: 'todo', priority: 'medium', progress: 0,
          assigneeId: 'a1', projectId: 'p1',
          createdAt: '2025-06-01', updatedAt: '2025-06-01'
        },
        {
          id: '2', name: 'Task 2', description: '',
          startDate: '2025-06-05', endDate: '2025-06-20',
          status: 'in-progress', priority: 'high', progress: 50,
          assigneeId: 'a2', projectId: 'p1',
          createdAt: '2025-06-05', updatedAt: '2025-06-05'
        }
      ]
      const result = calculateDateRange(tasks)
      // Should have start before first task and end after last task (with padding)
      expect(result.start < new Date('2025-06-01')).toBe(true)
      expect(result.end > new Date('2025-06-20')).toBe(true)
      expect(result.days).toBeGreaterThanOrEqual(14)
    })
  })

  describe('calculateTaskBarPosition', () => {
    it('calculates correct left and width', () => {
      const task: Task = {
        id: '1', name: 'Task', description: '',
        startDate: '2025-01-05', endDate: '2025-01-10',
        status: 'todo', priority: 'medium', progress: 0,
        assigneeId: 'a1', projectId: 'p1',
        createdAt: '2025-01-05', updatedAt: '2025-01-05'
      }
      const rangeStart = new Date('2025-01-01')
      const totalDays = 30

      const result = calculateTaskBarPosition(task, rangeStart, totalDays)

      expect(result.left).toBeGreaterThan(0)
      expect(result.width).toBeGreaterThan(0)
      expect(result.left + result.width).toBeLessThanOrEqual(100)
    })

    it('clamps left to 0 minimum', () => {
      const task: Task = {
        id: '1', name: 'Task', description: '',
        startDate: '2024-12-25', endDate: '2025-01-05',
        status: 'todo', priority: 'medium', progress: 0,
        assigneeId: 'a1', projectId: 'p1',
        createdAt: '2024-12-25', updatedAt: '2024-12-25'
      }
      const rangeStart = new Date('2025-01-01')
      const result = calculateTaskBarPosition(task, rangeStart, 30)

      expect(result.left).toBe(0)
    })
  })

  describe('getStatusColor', () => {
    it('returns correct color for each status', () => {
      expect(getStatusColor('todo')).toBe('bg-status-todo')
      expect(getStatusColor('in-progress')).toBe('bg-status-in-progress')
      expect(getStatusColor('review')).toBe('bg-status-review')
      expect(getStatusColor('completed')).toBe('bg-status-completed')
    })
  })

  describe('getStatusLabel', () => {
    it('returns correct label for each status', () => {
      expect(getStatusLabel('todo')).toBe('To Do')
      expect(getStatusLabel('in-progress')).toBe('In Progress')
      expect(getStatusLabel('review')).toBe('In Review')
      expect(getStatusLabel('completed')).toBe('Completed')
    })
  })

  describe('formatDateForInput', () => {
    it('formats date to YYYY-MM-DD', () => {
      const date = new Date('2025-06-15T10:30:00Z')
      const result = formatDateForInput(date)
      expect(result).toBe('2025-06-15')
    })

    it('handles string input', () => {
      const result = formatDateForInput('2025-03-20')
      expect(result).toBe('2025-03-20')
    })
  })

  describe('generateTimelineHeader', () => {
    it('generates correct number of dates', () => {
      const start = new Date('2025-01-01')
      const result = generateTimelineHeader(start, 10)
      expect(result).toHaveLength(10)
    })

    it('generates consecutive dates', () => {
      const start = new Date('2025-01-01')
      const result = generateTimelineHeader(start, 5)
      for (let i = 1; i < result.length; i++) {
        const diff = getDaysBetween(result[i - 1], result[i])
        expect(diff).toBe(1)
      }
    })
  })

  describe('isWeekend', () => {
    it('returns true for Saturday', () => {
      // Use explicit local time to avoid timezone offset
      const saturday = new Date(2025, 0, 4, 12, 0, 0) // Jan 4, 2025 = Saturday
      expect(isWeekend(saturday)).toBe(true)
    })

    it('returns true for Sunday', () => {
      const sunday = new Date(2025, 0, 5, 12, 0, 0) // Jan 5, 2025 = Sunday
      expect(isWeekend(sunday)).toBe(true)
    })

    it('returns false for weekday', () => {
      const monday = new Date(2025, 0, 6, 12, 0, 0) // Jan 6, 2025 = Monday
      expect(isWeekend(monday)).toBe(false)
    })
  })

  describe('getStartOfWeek', () => {
    it('returns Monday for a mid-week date', () => {
      const wednesday = new Date(2025, 0, 8, 12, 0, 0) // Jan 8, 2025 = Wednesday
      const result = getStartOfWeek(wednesday)
      expect(result.getDay()).toBe(1) // Monday
    })

    it('returns same Monday for Monday input', () => {
      const monday = new Date(2025, 0, 6, 12, 0, 0) // Jan 6, 2025 = Monday
      const result = getStartOfWeek(monday)
      expect(result.getDay()).toBe(1) // Still Monday
      expect(result.getDate()).toBe(6)
    })
  })

  describe('getStartOfMonth', () => {
    it('returns first day of month', () => {
      const date = new Date('2025-06-15')
      const result = getStartOfMonth(date)
      expect(result.getDate()).toBe(1)
      expect(result.getMonth()).toBe(5) // June (0-indexed)
    })
  })

  describe('getWeekNumber', () => {
    it('returns 1 for first week of year', () => {
      const jan1 = new Date('2025-01-01')
      const weekNum = getWeekNumber(jan1)
      expect(weekNum).toBe(1)
    })

    it('returns value between 1 and 53', () => {
      const date = new Date('2025-06-15')
      const weekNum = getWeekNumber(date)
      expect(weekNum).toBeGreaterThanOrEqual(1)
      expect(weekNum).toBeLessThanOrEqual(53)
    })
  })

  describe('calculateTimelineUnits', () => {
    it('returns days for day view', () => {
      const start = new Date('2025-01-01')
      expect(calculateTimelineUnits(start, 30, 'day')).toBe(30)
    })

    it('returns weeks for week view', () => {
      const start = new Date('2025-01-01')
      expect(calculateTimelineUnits(start, 28, 'week')).toBe(4)
    })

    it('returns months for month view', () => {
      const start = new Date('2025-01-01')
      // 90 days spans ~3 months
      const months = calculateTimelineUnits(start, 90, 'month')
      expect(months).toBeGreaterThanOrEqual(3)
    })
  })

  describe('generateWeekTimeline', () => {
    it('generates week timeline items', () => {
      const start = new Date('2025-01-01')
      const items = generateWeekTimeline(start, 28)
      expect(items.length).toBeGreaterThan(0)
      items.forEach(item => {
        expect(item.label).toMatch(/^Sem \d+$/)
        expect(item.subLabel).toBeDefined()
      })
    })
  })

  describe('generateMonthTimeline', () => {
    it('generates month timeline items', () => {
      const start = new Date('2025-01-01')
      const items = generateMonthTimeline(start, 90)
      expect(items.length).toBeGreaterThan(0)
      items.forEach(item => {
        expect(item.label).toBeTruthy()
        expect(item.subLabel).toBeDefined()
      })
    })
  })
})
