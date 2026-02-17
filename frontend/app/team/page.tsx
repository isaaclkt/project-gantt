'use client'

import { useState, useCallback, useEffect } from 'react'
import useSWR, { mutate } from 'swr'
import { DashboardLayout } from '@/components/layout'
import { TeamMemberCard, TeamMemberFormDialog } from '@/components/team'
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
import { useRouter } from 'next/navigation'
import { Plus, Search, Users, Loader2 } from 'lucide-react'
import { TeamMember, CreateTeamMemberInput, MemberStatus } from '@/lib/types'
import {
  getTeamMembers,
  createTeamMember,
  updateTeamMember,
  deleteTeamMember
} from '@/lib/services'
import { useAuth } from '@/contexts/auth-context'
import { useSettings } from '@/contexts/settings-context'
import { canManageTeam } from '@/lib/permissions'

type StatusFilter = MemberStatus | 'all'
type DepartmentFilter = string | 'all'

const statusFilters: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'active', label: 'Ativo' },
  { value: 'away', label: 'Ausente' },
  { value: 'offline', label: 'Offline' }
]

// SWR fetcher
const teamFetcher = async () => {
  const response = await getTeamMembers()
  return response.data
}

export default function TeamPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const { settings } = useSettings()
  const showAvatars = settings?.displayPreferences?.showAvatars ?? true
  const userRole = user?.role
  const router = useRouter()

  const { data: teamMembers = [], isLoading } = useSWR('teamMembers', teamFetcher)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [authLoading, isAuthenticated, router])

  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [departmentFilter, setDepartmentFilter] = useState<DepartmentFilter>('all')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Get unique departments for filter
  const departments = Array.from(
    new Set(teamMembers.filter(m => m.department).map(m => m.department!))
  ).sort()

  // Filter team members
  const filteredMembers = teamMembers.filter(member => {
    const matchesSearch =
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.role.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || member.status === statusFilter
    const matchesDepartment =
      departmentFilter === 'all' || member.department === departmentFilter
    return matchesSearch && matchesStatus && matchesDepartment
  })

  // Group members by department
  const groupedMembers = filteredMembers.reduce(
    (acc, member) => {
      const dept = member.department || 'Other'
      if (!acc[dept]) {
        acc[dept] = []
      }
      acc[dept].push(member)
      return acc
    },
    {} as Record<string, TeamMember[]>
  )

  const handleCreateMember = useCallback(async (data: CreateTeamMemberInput) => {
    setIsSubmitting(true)
    try {
      await createTeamMember(data)
      await mutate('teamMembers')
      setIsFormOpen(false)
    } finally {
      setIsSubmitting(false)
    }
  }, [])

  const handleUpdateMember = useCallback(
    async (data: CreateTeamMemberInput) => {
      if (!selectedMember) return
      setIsSubmitting(true)
      try {
        await updateTeamMember({ id: selectedMember.id, ...data })
        await mutate('teamMembers')
        setIsFormOpen(false)
        setSelectedMember(null)
      } finally {
        setIsSubmitting(false)
      }
    },
    [selectedMember]
  )

  const handleDeleteMember = useCallback(async () => {
    if (!selectedMember) return
    setIsSubmitting(true)
    try {
      await deleteTeamMember(selectedMember.id)
      await mutate('teamMembers')
      setIsDeleteOpen(false)
      setSelectedMember(null)
    } finally {
      setIsSubmitting(false)
    }
  }, [selectedMember])

  const handleEdit = (member: TeamMember) => {
    setSelectedMember(member)
    setIsFormOpen(true)
  }

  const handleDelete = (member: TeamMember) => {
    setSelectedMember(member)
    setIsDeleteOpen(true)
  }

  const handleOpenCreate = () => {
    setSelectedMember(null)
    setIsFormOpen(true)
  }

  // Handlers memoizados para evitar re-renders
  const handleFormOpenChange = useCallback((open: boolean) => {
    setIsFormOpen(open)
    if (!open) setSelectedMember(null)
  }, [])

  const handleDeleteOpenChange = useCallback((open: boolean) => {
    setIsDeleteOpen(open)
  }, [])

  // Stats
  const stats = {
    total: teamMembers.length,
    active: teamMembers.filter(m => m.status === 'active').length,
    away: teamMembers.filter(m => m.status === 'away').length,
    offline: teamMembers.filter(m => m.status === 'offline').length
  }

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
            <h1 className="text-2xl font-bold text-foreground">Equipe</h1>
            <p className="text-muted-foreground">
              Gerencie os membros da equipe e seus papéis
            </p>
          </div>
          {userRole && canManageTeam(userRole) && (
            <Button onClick={handleOpenCreate}>
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Membro
            </Button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 bg-card border border-border rounded-lg">
            <p className="text-sm text-muted-foreground">Total de Membros</p>
            <p className="text-2xl font-bold text-foreground">{stats.total}</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-status-completed" />
              <p className="text-sm text-muted-foreground">Ativos</p>
            </div>
            <p className="text-2xl font-bold text-status-completed">{stats.active}</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-status-in-progress" />
              <p className="text-sm text-muted-foreground">Ausentes</p>
            </div>
            <p className="text-2xl font-bold text-status-in-progress">{stats.away}</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-muted-foreground" />
              <p className="text-sm text-muted-foreground">Offline</p>
            </div>
            <p className="text-2xl font-bold text-muted-foreground">{stats.offline}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por nome, email ou cargo..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <div className="flex gap-3">
            <Select
              value={statusFilter}
              onValueChange={value => setStatusFilter(value as StatusFilter)}
            >
              <SelectTrigger className="w-32">
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
            <Select
              value={departmentFilter}
              onValueChange={value => setDepartmentFilter(value as DepartmentFilter)}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Departamento" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os Departamentos</SelectItem>
                {departments.map(dept => (
                  <SelectItem key={dept} value={dept}>
                    {dept}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Team Members */}
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="h-40 bg-card border border-border rounded-lg animate-pulse"
              />
            ))}
          </div>
        ) : filteredMembers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="h-16 w-16 rounded-full bg-secondary flex items-center justify-center mb-4">
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">Nenhum membro encontrado</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || statusFilter !== 'all' || departmentFilter !== 'all'
                ? 'Tente ajustar sua busca ou filtros'
                : 'Comece adicionando seu primeiro membro da equipe'}
            </p>
            {!searchQuery && statusFilter === 'all' && departmentFilter === 'all' && userRole && canManageTeam(userRole) && (
              <Button onClick={handleOpenCreate}>
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Membro
              </Button>
            )}
          </div>
        ) : departmentFilter === 'all' ? (
          // Grouped view by department
          <div className="space-y-8">
            {Object.entries(groupedMembers)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([department, members]) => (
                <div key={department}>
                  <h3 className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
                    {department}
                    <span className="text-xs bg-secondary px-2 py-0.5 rounded-full">
                      {members.length}
                    </span>
                  </h3>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {members.map(member => (
                      <TeamMemberCard
                        key={member.id}
                        member={member}
                        onEdit={userRole && canManageTeam(userRole) ? handleEdit : undefined}
                        onDelete={userRole && canManageTeam(userRole) ? handleDelete : undefined}
                        showAvatars={showAvatars}
                      />
                    ))}
                  </div>
                </div>
              ))}
          </div>
        ) : (
          // Flat view when filtering by department
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredMembers.map(member => (
              <TeamMemberCard
                key={member.id}
                member={member}
                onEdit={userRole && canManageTeam(userRole) ? handleEdit : undefined}
                onDelete={userRole && canManageTeam(userRole) ? handleDelete : undefined}
              />
            ))}
          </div>
        )}
      </div>

      {/* Team Member Form Dialog - Renderização condicional */}
      {isFormOpen && (
        <TeamMemberFormDialog
          open={isFormOpen}
          onOpenChange={handleFormOpenChange}
          member={selectedMember}
          onSubmit={selectedMember ? handleUpdateMember : handleCreateMember}
          isLoading={isSubmitting}
        />
      )}

      {/* Delete Confirmation Dialog - Renderização condicional */}
      {isDeleteOpen && (
        <AlertDialog open={isDeleteOpen} onOpenChange={handleDeleteOpenChange}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Remover Membro</AlertDialogTitle>
              <AlertDialogDescription>
                Tem certeza que deseja remover &quot;{selectedMember?.name}&quot; da equipe? Esta
                ação não pode ser desfeita.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancelar</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDeleteMember}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isSubmitting ? 'Removendo...' : 'Remover'}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      )}
    </DashboardLayout>
  )
}
