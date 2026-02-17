'use client'

import { useState } from 'react'
import { UserSettings } from '@/lib/types'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Loader2, Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from 'next-themes'
import { cn } from '@/lib/utils'

interface PreferencesSectionProps {
  settings: UserSettings
  onUpdate: (updates: Partial<Omit<UserSettings, 'id' | 'userId'>>) => Promise<void>
  isLoading?: boolean
}

const themeOptions: { value: UserSettings['theme']; label: string; icon: React.ElementType }[] = [
  { value: 'light', label: 'Claro', icon: Sun },
  { value: 'dark', label: 'Escuro', icon: Moon },
  { value: 'system', label: 'Sistema', icon: Monitor }
]

const languageOptions = [
  { value: 'pt-BR', label: 'Português (BR)' },
  { value: 'en-US', label: 'Inglês (EUA)' },
  { value: 'es-ES', label: 'Espanhol' },
  { value: 'fr-FR', label: 'Francês' },
  { value: 'de-DE', label: 'Alemão' }
]

const defaultViewOptions: { value: UserSettings['displayPreferences']['defaultView']; label: string }[] = [
  { value: 'gantt', label: 'Gráfico Gantt' },
  { value: 'list', label: 'Lista' },
  { value: 'board', label: 'Quadro' }
]

export function PreferencesSection({ settings, onUpdate, isLoading }: PreferencesSectionProps) {
  const { setTheme } = useTheme()
  const [formData, setFormData] = useState({
    theme: settings.theme,
    language: settings.language,
    displayPreferences: { ...settings.displayPreferences }
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
    formData.theme !== settings.theme ||
    formData.language !== settings.language ||
    formData.displayPreferences.compactMode !== settings.displayPreferences.compactMode ||
    formData.displayPreferences.showAvatars !== settings.displayPreferences.showAvatars ||
    formData.displayPreferences.defaultView !== settings.displayPreferences.defaultView

  return (
    <Card>
      <CardHeader>
        <CardTitle>Preferências</CardTitle>
        <CardDescription>
          Personalize a aparência e o comportamento do ProjectFlow
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Theme Selection */}
          <div className="space-y-3">
            <Label>Tema</Label>
            <p className="text-sm text-muted-foreground">
              Selecione seu tema de cores preferido
            </p>
            <div className="grid grid-cols-3 gap-3">
              {themeOptions.map((option) => {
                const Icon = option.icon
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => {
                      setFormData(prev => ({ ...prev, theme: option.value }))
                      setTheme(option.value)
                    }}
                    className={cn(
                      'flex flex-col items-center gap-2 p-4 border rounded-lg transition-all',
                      formData.theme === option.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    )}
                  >
                    <Icon className={cn(
                      'h-5 w-5',
                      formData.theme === option.value ? 'text-primary' : 'text-muted-foreground'
                    )} />
                    <span className={cn(
                      'text-sm font-medium',
                      formData.theme === option.value ? 'text-primary' : 'text-foreground'
                    )}>
                      {option.label}
                    </span>
                  </button>
                )
              })}
            </div>
            <p className="text-xs text-muted-foreground">
              Selecione o tema visual da aplicação.
            </p>
          </div>

          {/* Language */}
          <div className="space-y-2">
            <Label>Idioma</Label>
            <Select
              value={formData.language}
              onValueChange={(value) => setFormData(prev => ({ ...prev, language: value }))}
            >
              <SelectTrigger className="w-full sm:w-64">
                <SelectValue placeholder="Selecione o idioma" />
              </SelectTrigger>
              <SelectContent>
                {languageOptions.map(lang => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Default View */}
          <div className="space-y-2">
            <Label>Visualização Padrão</Label>
            <Select
              value={formData.displayPreferences.defaultView}
              onValueChange={(value) =>
                setFormData(prev => ({
                  ...prev,
                  displayPreferences: { ...prev.displayPreferences, defaultView: value as UserSettings['displayPreferences']['defaultView'] }
                }))
              }
            >
              <SelectTrigger className="w-full sm:w-64">
                <SelectValue placeholder="Selecione a visualização" />
              </SelectTrigger>
              <SelectContent>
                {defaultViewOptions.map(view => (
                  <SelectItem key={view.value} value={view.value}>
                    {view.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Display Options */}
          <div className="space-y-4">
            <Label>Opções de Exibição</Label>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <p className="text-sm font-medium text-foreground">Modo Compacto</p>
                  <p className="text-sm text-muted-foreground">
                    Usar espaçamento menor e layouts condensados
                  </p>
                </div>
                <Switch
                  checked={formData.displayPreferences.compactMode}
                  onCheckedChange={(checked) =>
                    setFormData(prev => ({
                      ...prev,
                      displayPreferences: { ...prev.displayPreferences, compactMode: checked }
                    }))
                  }
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <p className="text-sm font-medium text-foreground">Mostrar Avatares</p>
                  <p className="text-sm text-muted-foreground">
                    Exibir avatares dos usuários em toda a aplicação
                  </p>
                </div>
                <Switch
                  checked={formData.displayPreferences.showAvatars}
                  onCheckedChange={(checked) =>
                    setFormData(prev => ({
                      ...prev,
                      displayPreferences: { ...prev.displayPreferences, showAvatars: checked }
                    }))
                  }
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <Button type="submit" disabled={!hasChanges || isSaving}>
              {isSaving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Salvar Preferências
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
