'use client'

import { useEffect } from 'react'
import useSWR, { mutate } from 'swr'
import { DashboardLayout } from '@/components/layout'
import { ProfileSection, PasswordSection, PreferencesSection, NotificationsSection } from '@/components/settings'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRouter } from 'next/navigation'
import { User, Settings as SettingsIcon, Bell, Lock, Loader2 } from 'lucide-react'
import { UserProfile, UserSettings } from '@/lib/types'
import { getUserProfile, updateUserProfile, updateUserSettings, changePassword, uploadAvatar } from '@/lib/services'
import { useToast } from '@/components/ui/use-toast'
import { useAuth } from '@/contexts/auth-context'
import { useSettings } from '@/contexts/settings-context'

// SWR fetchers
const profileFetcher = async () => {
  const response = await getUserProfile()
  return response.data
}

export default function SettingsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { settings, isLoading: settingsLoading, mutateSettings } = useSettings()
  const router = useRouter()
  const { toast } = useToast()
  const { data: profile, isLoading: profileLoading } = useSWR('userProfile', profileFetcher)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [authLoading, isAuthenticated, router])

  const handleUpdateProfile = async (
    updates: Partial<Omit<UserProfile, 'id' | 'joinedAt'>>
  ) => {
    try {
      const response = await updateUserProfile(updates)
      if (response.success) {
        await mutate('userProfile')
        toast({
          title: 'Perfil Atualizado',
          description: 'Suas informações foram salvas com sucesso.'
        })
      }
    } catch {
      toast({
        title: 'Erro',
        description: 'Falha ao atualizar perfil. Tente novamente.',
        variant: 'destructive'
      })
    }
  }

  const handleAvatarUpload = async (file: File) => {
    try {
      const response = await uploadAvatar(file)
      if (response.success) {
        await mutate('userProfile')
        toast({
          title: 'Avatar Atualizado',
          description: 'Sua foto de perfil foi alterada com sucesso.'
        })
      }
    } catch {
      toast({
        title: 'Erro',
        description: 'Falha ao enviar avatar. Verifique o formato e tamanho (máx. 5MB).',
        variant: 'destructive'
      })
    }
  }

  const handleChangePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    try {
      const response = await changePassword(currentPassword, newPassword)
      if (response.success) {
        toast({
          title: 'Senha Alterada',
          description: 'Sua senha foi alterada com sucesso.'
        })
        return true
      }
      return false
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Falha ao alterar senha. Tente novamente.'
      toast({
        title: 'Erro',
        description: message,
        variant: 'destructive'
      })
      return false
    }
  }

  const handleUpdateSettings = async (
    updates: Partial<Omit<UserSettings, 'id' | 'userId'>>
  ) => {
    try {
      const response = await updateUserSettings(updates)
      if (response.success) {
        mutateSettings()
        toast({
          title: 'Configurações Atualizadas',
          description: 'Suas preferências foram salvas com sucesso.'
        })
      }
    } catch {
      toast({
        title: 'Erro',
        description: 'Falha ao atualizar configurações. Tente novamente.',
        variant: 'destructive'
      })
    }
  }

  const isLoading = profileLoading || (settingsLoading && !settings)

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
        <div>
          <h1 className="text-2xl font-bold text-foreground">Configurações</h1>
          <p className="text-muted-foreground">
            Gerencie suas configurações e preferências
          </p>
        </div>

        {isLoading ? (
          <div className="space-y-6">
            {[...Array(3)].map((_, i) => (
              <div
                key={i}
                className="h-64 bg-card border border-border rounded-lg animate-pulse"
              />
            ))}
          </div>
        ) : profile && settings ? (
          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="grid w-full max-w-lg grid-cols-4">
              <TabsTrigger value="profile" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                <span className="hidden sm:inline">Perfil</span>
              </TabsTrigger>
              <TabsTrigger value="password" className="flex items-center gap-2">
                <Lock className="h-4 w-4" />
                <span className="hidden sm:inline">Senha</span>
              </TabsTrigger>
              <TabsTrigger value="preferences" className="flex items-center gap-2">
                <SettingsIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Preferências</span>
              </TabsTrigger>
              <TabsTrigger value="notifications" className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                <span className="hidden sm:inline">Notificações</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="space-y-6">
              <ProfileSection
                profile={profile}
                onUpdate={handleUpdateProfile}
                onAvatarUpload={handleAvatarUpload}
              />
            </TabsContent>

            <TabsContent value="password" className="space-y-6">
              <PasswordSection onChangePassword={handleChangePassword} />
            </TabsContent>

            <TabsContent value="preferences" className="space-y-6">
              <PreferencesSection
                settings={settings}
                onUpdate={handleUpdateSettings}
              />
            </TabsContent>

            <TabsContent value="notifications" className="space-y-6">
              <NotificationsSection
                settings={settings}
                onUpdate={handleUpdateSettings}
              />
            </TabsContent>
          </Tabs>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-muted-foreground">Falha ao carregar configurações. Tente novamente.</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
