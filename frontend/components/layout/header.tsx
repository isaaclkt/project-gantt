'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import useSWR from 'swr'
import {
  Bell, Search, Plus, ChevronDown, LogOut, Settings,
  CheckSquare, Clock, X, CheckCircle2,
  AlertTriangle, TrendingDown, UserCog, UserX, FolderClock,
  TrendingUp, Trophy, BarChart3, Info,
  type LucideIcon
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from '@/components/ui/popover'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useAuth } from '@/contexts/auth-context'
import { useSettings } from '@/contexts/settings-context'
import { Task, Project, TeamMember } from '@/lib/types'
import { getTasks, getProjects, getTeamMembers, getInsights } from '@/lib/services'
import type { Insight } from '@/lib/services/insights-service'
import { cn } from '@/lib/utils'

interface HeaderProps {
  onNewTask?: () => void
}

const roleLabels: Record<string, string> = {
  admin: 'Admin',
  manager: 'Gerente',
  member: 'Membro',
  viewer: 'Visualizador',
}

const roleColors: Record<string, string> = {
  admin: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  manager: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  member: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  viewer: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// Map insight icon names to Lucide components
const insightIconMap: Record<string, LucideIcon> = {
  AlertTriangle, FolderClock, UserX, Clock, UserCog,
  TrendingDown, CheckCircle2, TrendingUp,
  Trophy, BarChart3, Info,
}

// Convert insights to notification format
function insightsToNotifications(insights: Insight[]) {
  return insights.slice(0, 6).map((insight, i) => ({
    id: `insight-${i}`,
    icon: insightIconMap[insight.icon] || Info,
    title: insight.title,
    description: insight.description,
    read: insight.type === 'positive' || insight.type === 'info',
  }))
}

// SWR fetchers
const tasksFetcher = async () => { const r = await getTasks(); return r.data }
const projectsFetcher = async () => { const r = await getProjects(); return r.data }
const teamFetcher = async () => { const r = await getTeamMembers(); return r.data }
const insightsFetcher = async () => { const r = await getInsights(); return r.data?.insights || [] }

export function Header({ onNewTask }: HeaderProps) {
  const { user, logout } = useAuth()
  const { settings } = useSettings()
  const showAvatars = settings?.displayPreferences?.showAvatars ?? true
  const router = useRouter()
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const { data: tasks = [] } = useSWR('header-tasks', tasksFetcher, { revalidateOnFocus: false })
  const { data: projects = [] } = useSWR('header-projects', projectsFetcher, { revalidateOnFocus: false })
  const { data: teamMembers = [] } = useSWR('header-team', teamFetcher, { revalidateOnFocus: false })
  const { data: insights = [] } = useSWR<Insight[]>('header-insights', insightsFetcher, { revalidateOnFocus: false })

  // Keyboard shortcut Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setSearchOpen(true)
      }
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Filter search results
  const filteredTasks = searchQuery.length >= 2
    ? tasks.filter(t =>
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description?.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 5)
    : []

  const filteredProjects = searchQuery.length >= 2
    ? projects.filter(p =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 3)
    : []

  const filteredMembers = searchQuery.length >= 2
    ? teamMembers.filter(m =>
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.email.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 3)
    : []

  const hasResults = filteredTasks.length > 0 || filteredProjects.length > 0 || filteredMembers.length > 0

  const handleSearchSelect = useCallback((type: string, _id: string) => {
    setSearchOpen(false)
    setSearchQuery('')
    switch (type) {
      case 'project':
        router.push('/projects')
        break
      case 'team':
        router.push('/team')
        break
      default:
        router.push('/')
    }
  }, [router])

  const handleLogout = async () => {
    await logout()
  }

  const handleSettings = () => {
    router.push('/settings')
  }

  const notifications = insightsToNotifications(insights)
  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      {/* Search Bar - opens dialog */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <button
          onClick={() => setSearchOpen(true)}
          className="relative w-full flex items-center gap-2 px-3 py-2 rounded-md bg-secondary border border-border text-sm text-muted-foreground hover:bg-secondary/80 transition-colors"
        >
          <Search className="h-4 w-4" />
          <span>Buscar tarefas, projetos...</span>
          <kbd className="ml-auto hidden sm:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            Ctrl K
          </kbd>
        </button>
      </div>

      {/* Search Dialog */}
      <Dialog open={searchOpen} onOpenChange={setSearchOpen}>
        <DialogContent className="sm:max-w-[500px] p-0 gap-0">
          <DialogHeader className="px-4 pt-4 pb-0">
            <DialogTitle className="sr-only">Buscar</DialogTitle>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar tarefas, projetos, membros..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-10 border-0 border-b rounded-none focus-visible:ring-0"
                autoFocus
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </DialogHeader>

          <ScrollArea className="max-h-[300px]">
            {searchQuery.length < 2 ? (
              <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                Digite pelo menos 2 caracteres para buscar
              </div>
            ) : !hasResults ? (
              <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                Nenhum resultado encontrado para &quot;{searchQuery}&quot;
              </div>
            ) : (
              <div className="py-2">
                {filteredProjects.length > 0 && (
                  <div>
                    <p className="px-4 py-1.5 text-xs font-medium text-muted-foreground">Projetos</p>
                    {filteredProjects.map(project => (
                      <button
                        key={project.id}
                        onClick={() => handleSearchSelect('project', project.id)}
                        className="w-full flex items-center gap-3 px-4 py-2 hover:bg-accent text-left transition-colors"
                      >
                        <div className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: project.color }} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{project.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{project.description}</p>
                        </div>
                        <Badge variant="outline" className="text-xs shrink-0">{project.status}</Badge>
                      </button>
                    ))}
                  </div>
                )}

                {filteredTasks.length > 0 && (
                  <div>
                    <p className="px-4 py-1.5 text-xs font-medium text-muted-foreground">Tarefas</p>
                    {filteredTasks.map(task => (
                      <button
                        key={task.id}
                        onClick={() => handleSearchSelect('task', task.id)}
                        className="w-full flex items-center gap-3 px-4 py-2 hover:bg-accent text-left transition-colors"
                      >
                        <CheckSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{task.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{task.description}</p>
                        </div>
                        <Badge variant="outline" className="text-xs shrink-0">{task.status}</Badge>
                      </button>
                    ))}
                  </div>
                )}

                {filteredMembers.length > 0 && (
                  <div>
                    <p className="px-4 py-1.5 text-xs font-medium text-muted-foreground">Membros</p>
                    {filteredMembers.map(member => (
                      <button
                        key={member.id}
                        onClick={() => handleSearchSelect('team', member.id)}
                        className="w-full flex items-center gap-3 px-4 py-2 hover:bg-accent text-left transition-colors"
                      >
                        <Avatar className="h-6 w-6">
                          {showAvatars && (
                            <AvatarImage src={member.avatar || '/placeholder.svg'} />
                          )}
                          <AvatarFallback className="text-xs">{getInitials(member.name)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{member.name}</p>
                          <p className="text-xs text-muted-foreground truncate">{member.email}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* New Task Button */}
        {onNewTask && (
          <Button onClick={onNewTask} className="gap-2">
            <Plus className="h-4 w-4" />
            Nova Tarefa
          </Button>
        )}

        {/* Notifications */}
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-2 w-2 bg-primary rounded-full" />
              )}
              <span className="sr-only">Notificações</span>
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-80 p-0">
            <div className="px-4 py-3 border-b border-border">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold">Notificações</h4>
                {unreadCount > 0 && (
                  <Badge variant="secondary" className="text-xs">
                    {unreadCount} nova{unreadCount > 1 ? 's' : ''}
                  </Badge>
                )}
              </div>
            </div>
            <ScrollArea className="max-h-[300px]">
              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                  Nenhuma notificação
                </div>
              ) : (
                <div className="divide-y divide-border">
                  {notifications.map(notification => (
                    <div
                      key={notification.id}
                      className={cn(
                        'flex items-start gap-3 px-4 py-3 hover:bg-accent transition-colors cursor-pointer',
                        !notification.read && 'bg-primary/5'
                      )}
                    >
                      <div className="mt-0.5 h-8 w-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                        <notification.icon className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium">{notification.title}</p>
                        <p className="text-xs text-muted-foreground truncate">{notification.description}</p>
                      </div>
                      {!notification.read && (
                        <div className="mt-2 h-2 w-2 rounded-full bg-primary shrink-0" />
                      )}
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </PopoverContent>
        </Popover>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2 px-2">
              <Avatar className="h-8 w-8">
                {showAvatars && (
                  <AvatarImage src={user?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.name || 'User'}`} />
                )}
                <AvatarFallback>{user ? getInitials(user.name) : 'U'}</AvatarFallback>
              </Avatar>
              <div className="hidden md:flex flex-col items-start">
                <span className="text-sm font-medium">{user?.name || 'Usuário'}</span>
                {user && (
                  <Badge variant="outline" className={`text-xs ${roleColors[user.role]}`}>
                    {roleLabels[user.role]}
                  </Badge>
                )}
              </div>
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            {user && (
              <>
                <div className="px-2 py-1.5">
                  <p className="text-sm font-medium">{user.name}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                  {user.department && (
                    <p className="text-xs text-muted-foreground">{user.department}</p>
                  )}
                </div>
                <DropdownMenuSeparator />
              </>
            )}
            <DropdownMenuItem onClick={handleSettings}>
              <Settings className="mr-2 h-4 w-4" />
              Configurações
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-red-600">
              <LogOut className="mr-2 h-4 w-4" />
              Sair
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
