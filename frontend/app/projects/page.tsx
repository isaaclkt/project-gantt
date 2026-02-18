'use client'

import { useState, useCallback, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import useSWR, { mutate } from 'swr'
import { DashboardLayout } from '@/components/layout'
import { ProjectCard, ProjectFormDialog, ProjectDetailDialog, ShareDialog } from '@/components/projects'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog'
import { Plus, Search, LayoutGrid, List, Loader2 } from 'lucide-react'
import { Project, TeamMember, Task, CreateProjectInput, ProjectStatus } from '@/lib/types'
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
  getTeamMembers,
  getTasks
} from '@/lib/services'
import { cn } from '@/lib/utils'
import { useToast } from '@/components/ui/toast'
import { useAuth } from '@/contexts/auth-context'
import { canCreateProject, canEditProject, canDeleteProject, canShareProject } from '@/lib/permissions'

type ViewMode = 'grid' | 'list'

const statusFilters: { value: ProjectStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'planning', label: 'Planejamento' },
  { value: 'active', label: 'Ativo' },
  { value: 'on-hold', label: 'Pausado' },
  { value: 'completed', label: 'Concluído' }
]

// SWR fetchers
const projectsFetcher = async () => {
  const response = await getProjects()
  return response.data
}

const teamFetcher = async () => {
  const response = await getTeamMembers()
  return response.data
}

const tasksFetcher = async () => {
  const response = await getTasks()
  return response.data
}

export default function ProjectsPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const { toast } = useToast()
  const userRole = user?.role
  const router = useRouter()

  const { data: projects = [], isLoading: projectsLoading } = useSWR('projects', projectsFetcher)
  const { data: teamMembers = [] } = useSWR('teamMembers', teamFetcher)
  const { data: tasks = [] } = useSWR('tasks', tasksFetcher)

  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<ProjectStatus | 'all'>('all')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [isShareOpen, setIsShareOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [authLoading, isAuthenticated, router])

  // Filter projects
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleCreateProject = useCallback(async (data: CreateProjectInput) => {
    setIsSubmitting(true)
    try {
      await createProject(data)
      await mutate('projects')
      setIsFormOpen(false)
      toast({ title: 'Projeto criado', description: 'O projeto foi criado com sucesso.' })
    } catch {
      toast({ title: 'Erro ao criar', description: 'Não foi possível criar o projeto.', variant: 'destructive' })
    } finally {
      setIsSubmitting(false)
    }
  }, [toast])

  const handleUpdateProject = useCallback(async (data: CreateProjectInput) => {
    if (!selectedProject) return
    setIsSubmitting(true)
    try {
      await updateProject({ id: selectedProject.id, ...data })
      await mutate('projects')
      setIsFormOpen(false)
      setSelectedProject(null)
      toast({ title: 'Projeto atualizado', description: 'As alterações foram salvas.' })
    } catch {
      toast({ title: 'Erro ao atualizar', description: 'Não foi possível atualizar o projeto.', variant: 'destructive' })
    } finally {
      setIsSubmitting(false)
    }
  }, [selectedProject, toast])

  const handleDeleteProject = useCallback(async () => {
    if (!selectedProject) return
    setIsSubmitting(true)
    try {
      await deleteProject(selectedProject.id)
      await mutate('projects')
      setIsDeleteOpen(false)
      setSelectedProject(null)
      toast({
        title: 'Projeto excluído',
        description: 'O projeto foi removido com sucesso.',
      })
    } catch {
      await mutate('projects')
      setIsDeleteOpen(false)
      setSelectedProject(null)
      toast({
        title: 'Erro ao excluir',
        description: 'Não foi possível excluir o projeto. Tente novamente.',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }, [selectedProject, toast])

  const handleView = (project: Project) => {
    setSelectedProject(project)
    setIsDetailOpen(true)
  }

  const handleEdit = (project: Project) => {
    setSelectedProject(project)
    setIsFormOpen(true)
  }

  const handleDelete = (project: Project) => {
    setSelectedProject(project)
    setIsDeleteOpen(true)
  }

  const handleShare = (project: Project) => {
    setSelectedProject(project)
    setIsShareOpen(true)
  }

  const handleOpenCreate = () => {
    setSelectedProject(null)
    setIsFormOpen(true)
  }

  // Handlers memoizados para evitar re-renders
  const handleFormOpenChange = useCallback((open: boolean) => {
    setIsFormOpen(open)
    if (!open) setSelectedProject(null)
  }, [])

  const handleDetailOpenChange = useCallback((open: boolean) => {
    setIsDetailOpen(open)
  }, [])

  const handleDeleteOpenChange = useCallback((open: boolean) => {
    setIsDeleteOpen(open)
  }, [])

  const handleShareOpenChange = useCallback((open: boolean) => {
    setIsShareOpen(open)
    if (!open) setSelectedProject(null)
  }, [])

  if (authLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </DashboardLayout>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Projetos</h1>
            <p className="text-muted-foreground">
              Gerencie e acompanhe todos os seus projetos
            </p>
          </div>
          {userRole && canCreateProject(userRole) && (
            <Button onClick={handleOpenCreate}>
              <Plus className="h-4 w-4 mr-2" />
              Novo Projeto
            </Button>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-1 gap-3 max-w-md">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar projetos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select
              value={statusFilter}
              onValueChange={(value) => setStatusFilter(value as ProjectStatus | 'all')}
            >
              <SelectTrigger className="w-36">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                {statusFilters.map(filter => (
                  <SelectItem key={filter.value} value={filter.value}>
                    {filter.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-1 border border-border rounded-md p-1">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Projects Grid/List */}
        {projectsLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="h-64 bg-card border border-border rounded-lg animate-pulse"
              />
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="h-16 w-16 rounded-full bg-secondary flex items-center justify-center mb-4">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">Nenhum projeto encontrado</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || statusFilter !== 'all'
                ? 'Tente ajustar sua busca ou filtro'
                : 'Comece criando seu primeiro projeto'}
            </p>
            {!searchQuery && statusFilter === 'all' && userRole && canCreateProject(userRole) && (
              <Button onClick={handleOpenCreate}>
                <Plus className="h-4 w-4 mr-2" />
                Criar Projeto
              </Button>
            )}
          </div>
        ) : (
          <div
            className={cn(
              'grid gap-4',
              viewMode === 'grid'
                ? 'sm:grid-cols-2 lg:grid-cols-3'
                : 'grid-cols-1'
            )}
          >
            {filteredProjects.map(project => (
              <ProjectCard
                key={project.id}
                project={project}
                teamMembers={teamMembers}
                onView={handleView}
                onEdit={userRole && canEditProject(userRole) ? handleEdit : undefined}
                onDelete={userRole && canDeleteProject(userRole) ? handleDelete : undefined}
                onShare={userRole && canShareProject(userRole) ? handleShare : undefined}
              />
            ))}
          </div>
        )}
      </div>

      {/* Project Form Dialog - Renderização condicional */}
      {isFormOpen && (
        <ProjectFormDialog
          open={isFormOpen}
          onOpenChange={handleFormOpenChange}
          project={selectedProject}
          teamMembers={teamMembers}
          onSubmit={selectedProject ? handleUpdateProject : handleCreateProject}
          isLoading={isSubmitting}
        />
      )}

      {/* Project Detail Dialog - Renderização condicional */}
      {isDetailOpen && (
        <ProjectDetailDialog
          open={isDetailOpen}
          onOpenChange={handleDetailOpenChange}
          project={selectedProject}
          teamMembers={teamMembers}
          tasks={tasks}
        />
      )}

      {/* Delete Confirmation Dialog - Renderização condicional */}
      {isDeleteOpen && (
        <AlertDialog open={isDeleteOpen} onOpenChange={handleDeleteOpenChange}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Excluir Projeto</AlertDialogTitle>
                <AlertDialogDescription>
                  Tem certeza que deseja excluir &quot;{selectedProject?.name}&quot;? Esta ação não pode
                  ser desfeita e removerá todos os dados associados.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDeleteProject}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  {isSubmitting ? 'Excluindo...' : 'Excluir'}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
      )}

      {/* Share Dialog */}
      {isShareOpen && (
        <ShareDialog
          open={isShareOpen}
          onOpenChange={handleShareOpenChange}
          project={selectedProject}
        />
      )}
    </DashboardLayout>
  )
}
