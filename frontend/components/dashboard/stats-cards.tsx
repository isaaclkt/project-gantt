'use client'

import { Task } from '@/lib/types'
import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle2, Clock, AlertCircle, ListTodo } from 'lucide-react'

interface StatsCardsProps {
  tasks: Task[]
}

/**
 * Stats Cards Component
 * 
 * Dashboard statistics overview cards.
 */
export function StatsCards({ tasks }: StatsCardsProps) {
  const stats = {
    total: tasks.length,
    todo: tasks.filter((t) => t.status === 'todo').length,
    inProgress: tasks.filter((t) => t.status === 'in-progress').length,
    completed: tasks.filter((t) => t.status === 'completed').length
  }

  const cards = [
    {
      title: 'Total de Tarefas',
      value: stats.total,
      icon: ListTodo,
      color: 'text-primary',
      bgColor: 'bg-primary/10'
    },
    {
      title: 'A Fazer',
      value: stats.todo,
      icon: AlertCircle,
      color: 'text-status-todo',
      bgColor: 'bg-status-todo/10'
    },
    {
      title: 'Em Progresso',
      value: stats.inProgress,
      icon: Clock,
      color: 'text-status-in-progress',
      bgColor: 'bg-status-in-progress/10'
    },
    {
      title: 'Concluídas',
      value: stats.completed,
      icon: CheckCircle2,
      color: 'text-status-completed',
      bgColor: 'bg-status-completed/10'
    }
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title} className="border-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{card.title}</p>
                <p className="text-2xl font-bold mt-1">{card.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${card.bgColor}`}>
                <card.icon className={`h-5 w-5 ${card.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
