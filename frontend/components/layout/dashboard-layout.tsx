'use client'

import { ReactNode } from 'react'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { useSettings } from '@/contexts/settings-context'
import { cn } from '@/lib/utils'

interface DashboardLayoutProps {
  children: ReactNode
  onNewTask?: () => void
}

/**
 * Dashboard Layout Component
 *
 * Main layout wrapper with sidebar and header.
 * All dashboard pages should be wrapped with this component.
 */
export function DashboardLayout({ children, onNewTask }: DashboardLayoutProps) {
  const { settings } = useSettings()
  const isCompact = settings?.displayPreferences?.compactMode ?? false

  return (
    <div className={cn("h-screen flex bg-background overflow-hidden", isCompact && "compact")}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onNewTask={onNewTask} />
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
