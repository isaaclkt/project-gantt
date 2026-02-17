'use client'

import React from "react"

import { useState } from 'react'
import { UserSettings } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Loader2, Mail, Bell, Clock, FolderKanban } from 'lucide-react'

interface NotificationsSectionProps {
  settings: UserSettings
  onUpdate: (updates: Partial<Omit<UserSettings, 'id' | 'userId'>>) => Promise<void>
  isLoading?: boolean
}

export function NotificationsSection({ settings, onUpdate, isLoading }: NotificationsSectionProps) {
  const [formData, setFormData] = useState({
    notifications: { ...settings.notifications }
  })
  const [isSaving, setIsSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    try {
      await onUpdate(formData)
    } finally {
      setIsSaving(false)
    }
  }

  const hasChanges =
    formData.notifications.email !== settings.notifications.email ||
    formData.notifications.push !== settings.notifications.push ||
    formData.notifications.taskReminders !== settings.notifications.taskReminders ||
    formData.notifications.projectUpdates !== settings.notifications.projectUpdates

  const toggleNotification = (key: keyof UserSettings['notifications']) => {
    setFormData(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }))
  }

  const notificationItems = [
    {
      key: 'email' as const,
      icon: Mail,
      title: 'Notificações por E-mail',
      description: 'Receber notificações via e-mail'
    },
    {
      key: 'push' as const,
      icon: Bell,
      title: 'Notificações Push',
      description: 'Receber notificações push no navegador'
    },
    {
      key: 'taskReminders' as const,
      icon: Clock,
      title: 'Lembretes de Tarefas',
      description: 'Receber lembretes de prazos de tarefas'
    },
    {
      key: 'projectUpdates' as const,
      icon: FolderKanban,
      title: 'Atualizações de Projetos',
      description: 'Ficar informado sobre o progresso dos projetos'
    }
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Notificações</CardTitle>
        <CardDescription>
          Gerencie como e quando você recebe notificações
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            {notificationItems.map((item) => {
              const Icon = item.icon
              return (
                <div
                  key={item.key}
                  className="flex items-center justify-between p-4 border border-border rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-secondary flex items-center justify-center">
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div className="space-y-0.5">
                      <p className="font-medium text-foreground">{item.title}</p>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                  </div>
                  <Switch
                    checked={formData.notifications[item.key]}
                    onCheckedChange={() => toggleNotification(item.key)}
                  />
                </div>
              )
            })}
          </div>

          <div className="flex justify-end">
            <Button type="submit" disabled={!hasChanges || isSaving}>
              {isSaving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Salvar Notificações
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
