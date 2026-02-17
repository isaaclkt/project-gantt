'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Plus, Pencil, Trash2, Building2, Briefcase, Loader2, ShieldAlert } from 'lucide-react'
import {
  getDepartments,
  getRoles,
  createDepartment,
  createRole,
  updateDepartment,
  updateRole,
  deleteDepartment,
  deleteRole,
  Department,
  Role
} from '@/lib/services/admin-service'
import { useAuth } from '@/contexts/auth-context'
import { useToast } from '@/components/ui/toast'
import { ApiError, getErrorMessage } from '@/lib/api-config'

export default function AdminPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const { toast } = useToast()

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [authLoading, isAuthenticated, router])

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && isAuthenticated && user && user.role !== 'admin') {
      toast({
        title: 'Acesso Negado',
        description: 'Apenas administradores podem acessar esta página.',
        variant: 'destructive',
      })
      router.push('/')
    }
  }, [authLoading, isAuthenticated, user, router, toast])
  const [departments, setDepartments] = useState<Department[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)

  // Dialog states
  const [deptDialogOpen, setDeptDialogOpen] = useState(false)
  const [roleDialogOpen, setRoleDialogOpen] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [editingRole, setEditingRole] = useState<Role | null>(null)

  // Delete confirmation state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'dept' | 'role'; id: string; name: string } | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Form states
  const [deptName, setDeptName] = useState('')
  const [deptDescription, setDeptDescription] = useState('')
  const [roleName, setRoleName] = useState('')
  const [roleDescription, setRoleDescription] = useState('')

  const fetchData = async () => {
    setLoading(true)
    try {
      const [deptRes, roleRes] = await Promise.all([
        getDepartments(),
        getRoles()
      ])
      if (deptRes.success) setDepartments(deptRes.data)
      if (roleRes.success) setRoles(roleRes.data)
    } catch (error) {
      const message = error instanceof ApiError ? getErrorMessage(error) : 'Erro ao carregar dados'
      toast({
        title: 'Erro',
        description: message,
        variant: 'destructive',
      })
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Department handlers
  const openDeptDialog = (dept?: Department) => {
    if (dept) {
      setEditingDept(dept)
      setDeptName(dept.name)
      setDeptDescription(dept.description || '')
    } else {
      setEditingDept(null)
      setDeptName('')
      setDeptDescription('')
    }
    setDeptDialogOpen(true)
  }

  const handleDeptSubmit = async () => {
    try {
      if (editingDept) {
        await updateDepartment(editingDept.id, { name: deptName, description: deptDescription })
      } else {
        await createDepartment({ name: deptName, description: deptDescription })
      }
      setDeptDialogOpen(false)
      toast({ title: 'Sucesso', description: 'Departamento salvo com sucesso!', variant: 'success' })
      fetchData()
    } catch (error) {
      const message = error instanceof ApiError ? getErrorMessage(error) : 'Erro ao salvar departamento'
      toast({ title: 'Erro', description: message, variant: 'destructive' })
    }
  }

  const handleDeptDelete = (id: string) => {
    const dept = departments.find(d => d.id === id)
    setDeleteTarget({ type: 'dept', id, name: dept?.name || '' })
    setDeleteDialogOpen(true)
  }

  // Role handlers
  const openRoleDialog = (role?: Role) => {
    if (role) {
      setEditingRole(role)
      setRoleName(role.name)
      setRoleDescription(role.description || '')
    } else {
      setEditingRole(null)
      setRoleName('')
      setRoleDescription('')
    }
    setRoleDialogOpen(true)
  }

  const handleRoleSubmit = async () => {
    try {
      if (editingRole) {
        await updateRole(editingRole.id, { name: roleName, description: roleDescription })
      } else {
        await createRole({ name: roleName, description: roleDescription })
      }
      setRoleDialogOpen(false)
      toast({ title: 'Sucesso', description: 'Função salva com sucesso!', variant: 'success' })
      fetchData()
    } catch (error) {
      const message = error instanceof ApiError ? getErrorMessage(error) : 'Erro ao salvar função'
      toast({ title: 'Erro', description: message, variant: 'destructive' })
    }
  }

  const handleRoleDelete = (id: string) => {
    const role = roles.find(r => r.id === id)
    setDeleteTarget({ type: 'role', id, name: role?.name || '' })
    setDeleteDialogOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (!deleteTarget) return
    setIsDeleting(true)
    try {
      if (deleteTarget.type === 'dept') {
        await deleteDepartment(deleteTarget.id)
        toast({ title: 'Sucesso', description: 'Departamento excluído!', variant: 'success' })
      } else {
        await deleteRole(deleteTarget.id)
        toast({ title: 'Sucesso', description: 'Função excluída!', variant: 'success' })
      }
      fetchData()
    } catch (error) {
      const label = deleteTarget.type === 'dept' ? 'departamento' : 'função'
      const message = error instanceof ApiError ? getErrorMessage(error) : `Erro ao excluir ${label}`
      toast({ title: 'Erro', description: message, variant: 'destructive' })
    } finally {
      setIsDeleting(false)
      setDeleteDialogOpen(false)
      setDeleteTarget(null)
    }
  }

  // Handlers memoizados para evitar re-renders
  const handleDeptDialogChange = useCallback((open: boolean) => {
    setDeptDialogOpen(open)
    if (!open) {
      setEditingDept(null)
      setDeptName('')
      setDeptDescription('')
    }
  }, [])

  const handleRoleDialogChange = useCallback((open: boolean) => {
    setRoleDialogOpen(open)
    if (!open) {
      setEditingRole(null)
      setRoleName('')
      setRoleDescription('')
    }
  }, [])

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    )
  }

  // Don't render if not authenticated or not admin
  if (!isAuthenticated || !user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <ShieldAlert className="h-12 w-12 text-destructive" />
          <p className="text-muted-foreground">Acesso não autorizado</p>
        </div>
      </div>
    )
  }

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Administração</h1>
          <p className="text-muted-foreground">Gerencie departamentos e funções do sistema</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Departments Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  <CardTitle>Departamentos</CardTitle>
                </div>
                <Button size="sm" onClick={() => openDeptDialog()}>
                  <Plus className="h-4 w-4 mr-1" />
                  Novo
                </Button>
              </div>
              <CardDescription>
                Cadastre os departamentos da empresa
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-muted-foreground">Carregando...</p>
              ) : departments.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  Nenhum departamento cadastrado
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead className="w-[100px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {departments.map(dept => (
                      <TableRow key={dept.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{dept.name}</p>
                            {dept.description && (
                              <p className="text-sm text-muted-foreground">{dept.description}</p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openDeptDialog(dept)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeptDelete(dept.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          {/* Roles Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Briefcase className="h-5 w-5" />
                  <CardTitle>Funções</CardTitle>
                </div>
                <Button size="sm" onClick={() => openRoleDialog()}>
                  <Plus className="h-4 w-4 mr-1" />
                  Nova
                </Button>
              </div>
              <CardDescription>
                Cadastre as funções/cargos disponíveis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <p className="text-muted-foreground">Carregando...</p>
              ) : roles.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  Nenhuma função cadastrada
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead className="w-[100px]">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {roles.map(role => (
                      <TableRow key={role.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{role.name}</p>
                            {role.description && (
                              <p className="text-sm text-muted-foreground">{role.description}</p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => openRoleDialog(role)}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRoleDelete(role.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Department Dialog - Renderização condicional */}
        {deptDialogOpen && (
          <Dialog open={deptDialogOpen} onOpenChange={handleDeptDialogChange}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingDept ? 'Editar Departamento' : 'Novo Departamento'}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="deptName">Nome</Label>
                  <Input
                    id="deptName"
                    value={deptName}
                    onChange={(e) => setDeptName(e.target.value)}
                    placeholder="Ex: Tecnologia"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="deptDesc">Descrição (opcional)</Label>
                  <Input
                    id="deptDesc"
                    value={deptDescription}
                    onChange={(e) => setDeptDescription(e.target.value)}
                    placeholder="Descrição do departamento"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => handleDeptDialogChange(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleDeptSubmit} disabled={!deptName.trim()}>
                  {editingDept ? 'Salvar' : 'Criar'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}

        {/* Role Dialog - Renderização condicional */}
        {roleDialogOpen && (
          <Dialog open={roleDialogOpen} onOpenChange={handleRoleDialogChange}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  {editingRole ? 'Editar Função' : 'Nova Função'}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="roleName">Nome</Label>
                  <Input
                    id="roleName"
                    value={roleName}
                    onChange={(e) => setRoleName(e.target.value)}
                    placeholder="Ex: Desenvolvedor Frontend"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="roleDesc">Descrição (opcional)</Label>
                  <Input
                    id="roleDesc"
                    value={roleDescription}
                    onChange={(e) => setRoleDescription(e.target.value)}
                    placeholder="Descrição da função"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => handleRoleDialogChange(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleRoleSubmit} disabled={!roleName.trim()}>
                  {editingRole ? 'Salvar' : 'Criar'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
        {/* Delete Confirmation Dialog */}
        {deleteDialogOpen && (
          <AlertDialog open={deleteDialogOpen} onOpenChange={(open) => {
            setDeleteDialogOpen(open)
            if (!open) setDeleteTarget(null)
          }}>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>
                  Excluir {deleteTarget?.type === 'dept' ? 'Departamento' : 'Função'}
                </AlertDialogTitle>
                <AlertDialogDescription>
                  Tem certeza que deseja excluir &quot;{deleteTarget?.name}&quot;? Esta ação não pode ser desfeita.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleConfirmDelete}
                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  {isDeleting ? 'Excluindo...' : 'Excluir'}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
      </div>
    </DashboardLayout>
  )
}
