'use client'

import React from "react"

import { useState, useEffect } from 'react'
import { TeamMember, CreateTeamMemberInput, MemberStatus } from '@/lib/types'
import { getDepartments, getRoles, Department, Role } from '@/lib/services/admin-service'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

interface TeamMemberFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  member?: TeamMember | null
  onSubmit: (data: CreateTeamMemberInput) => void
  isLoading?: boolean
}

const statusOptions: { value: MemberStatus; label: string }[] = [
  { value: 'active', label: 'Ativo' },
  { value: 'away', label: 'Ausente' },
  { value: 'offline', label: 'Offline' }
]

export function TeamMemberFormDialog({
  open,
  onOpenChange,
  member,
  onSubmit,
  isLoading
}: TeamMemberFormDialogProps) {
  const [formData, setFormData] = useState<CreateTeamMemberInput>({
    name: '',
    email: '',
    role: '',
    department: '',
    status: 'active'
  })

  const [departments, setDepartments] = useState<Department[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loadingOptions, setLoadingOptions] = useState(true)

  // Fetch departments and roles from API - usando ref para evitar loop
  const hasFetched = React.useRef(false)

  useEffect(() => {
    // Reset quando o dialog fecha
    if (!open) {
      hasFetched.current = false
      return
    }

    // Evita fetch duplicado
    if (hasFetched.current) return
    hasFetched.current = true

    async function fetchOptions() {
      setLoadingOptions(true)
      try {
        const [deptResponse, rolesResponse] = await Promise.all([
          getDepartments(),
          getRoles()
        ])
        if (deptResponse.success) {
          setDepartments(deptResponse.data)
        }
        if (rolesResponse.success) {
          setRoles(rolesResponse.data)
        }
      } catch {
        // options will remain empty
      }
      setLoadingOptions(false)
    }

    fetchOptions()
  }, [open])

  useEffect(() => {
    if (member) {
      setFormData({
        name: member.name,
        email: member.email,
        role: member.role,
        department: member.department || '',
        status: member.status
      })
    } else {
      setFormData({
        name: '',
        email: '',
        role: '',
        department: '',
        status: 'active'
      })
    }
  }, [member])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>
            {member ? 'Editar Membro' : 'Adicionar Novo Membro'}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Nome Completo</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Digite o nome completo"
                required
              />
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="email@empresa.com"
                required
              />
            </div>

            {/* Role */}
            <div className="space-y-2">
              <Label>Função</Label>
              <Select
                value={formData.role}
                onValueChange={(value) => setFormData(prev => ({ ...prev, role: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder={loadingOptions ? "Carregando..." : "Selecione a função"} />
                </SelectTrigger>
                <SelectContent>
                  {roles.length === 0 && !loadingOptions ? (
                    <SelectItem value="_empty" disabled>
                      Nenhuma função cadastrada
                    </SelectItem>
                  ) : (
                    roles.map(role => (
                      <SelectItem key={role.id} value={role.name}>
                        {role.name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Department */}
            <div className="space-y-2">
              <Label>Departamento</Label>
              <Select
                value={formData.department || ''}
                onValueChange={(value) => setFormData(prev => ({ ...prev, department: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder={loadingOptions ? "Carregando..." : "Selecione o departamento"} />
                </SelectTrigger>
                <SelectContent>
                  {departments.length === 0 && !loadingOptions ? (
                    <SelectItem value="_empty" disabled>
                      Nenhum departamento cadastrado
                    </SelectItem>
                  ) : (
                    departments.map(dept => (
                      <SelectItem key={dept.id} value={dept.name}>
                        {dept.name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label>Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value: MemberStatus) =>
                  setFormData(prev => ({ ...prev, status: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading || loadingOptions}>
              {isLoading ? 'Salvando...' : member ? 'Salvar' : 'Adicionar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
