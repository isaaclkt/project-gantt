'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  AlertTriangle,
  FolderClock,
  UserX,
  Clock,
  UserCog,
  TrendingDown,
  CheckCircle2,
  TrendingUp,
  Trophy,
  BarChart3,
  Info,
  Lightbulb,
  ChevronDown,
  ChevronUp,
  type LucideIcon
} from 'lucide-react'
import type { Insight } from '@/lib/services/insights-service'

// Map icon string names to actual Lucide components
const iconMap: Record<string, LucideIcon> = {
  AlertTriangle,
  FolderClock,
  UserX,
  Clock,
  UserCog,
  TrendingDown,
  CheckCircle2,
  TrendingUp,
  Trophy,
  BarChart3,
  Info,
}

const typeConfig = {
  critical: {
    border: 'border-l-red-500',
    bg: 'bg-red-500/10',
    text: 'text-red-500',
    badge: 'bg-red-500/15 text-red-600 border-red-500/20',
    label: 'Crítico',
  },
  warning: {
    border: 'border-l-yellow-500',
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-500',
    badge: 'bg-yellow-500/15 text-yellow-600 border-yellow-500/20',
    label: 'Atenção',
  },
  positive: {
    border: 'border-l-green-500',
    bg: 'bg-green-500/10',
    text: 'text-green-500',
    badge: 'bg-green-500/15 text-green-600 border-green-500/20',
    label: 'Positivo',
  },
  info: {
    border: 'border-l-blue-500',
    bg: 'bg-blue-500/10',
    text: 'text-blue-500',
    badge: 'bg-blue-500/15 text-blue-600 border-blue-500/20',
    label: 'Info',
  },
}

interface InsightsPanelProps {
  insights: Insight[]
}

export function InsightsPanel({ insights }: InsightsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (insights.length === 0) {
    return null
  }

  const criticalCount = insights.filter(i => i.type === 'critical').length
  const warningCount = insights.filter(i => i.type === 'warning').length

  return (
    <Card className="border-border">
      <CardContent className="p-0">
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors rounded-t-lg"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Lightbulb className="h-5 w-5 text-primary" />
            </div>
            <div className="text-left">
              <h3 className="text-sm font-semibold">Insights Inteligentes</h3>
              <p className="text-xs text-muted-foreground">
                {insights.length} insight{insights.length > 1 ? 's' : ''} encontrado{insights.length > 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
              <Badge variant="outline" className={typeConfig.critical.badge}>
                {criticalCount} crítico{criticalCount > 1 ? 's' : ''}
              </Badge>
            )}
            {warningCount > 0 && (
              <Badge variant="outline" className={typeConfig.warning.badge}>
                {warningCount} alerta{warningCount > 1 ? 's' : ''}
              </Badge>
            )}
            {isExpanded ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        </button>

        {/* Insights List */}
        {isExpanded && (
          <div className="px-4 pb-4 space-y-2">
            {insights.map((insight, index) => {
              const config = typeConfig[insight.type]
              const IconComponent = iconMap[insight.icon] || Info

              return (
                <div
                  key={index}
                  className={`flex items-start gap-3 p-3 rounded-lg border-l-4 ${config.border} bg-card hover:bg-muted/30 transition-colors`}
                >
                  <div className={`p-1.5 rounded-md ${config.bg} shrink-0 mt-0.5`}>
                    <IconComponent className={`h-4 w-4 ${config.text}`} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{insight.title}</p>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                      {insight.description}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
