'use client'

import React, { createContext, useContext } from 'react'
import useSWR from 'swr'
import { UserSettings } from '@/lib/types'
import { getUserSettings, updateUserSettings } from '@/lib/services'

interface SettingsContextValue {
  settings: UserSettings | null
  isLoading: boolean
  updateSettings: (updates: Partial<Omit<UserSettings, 'id' | 'userId'>>) => Promise<void>
  mutateSettings: () => void
}

const SettingsContext = createContext<SettingsContextValue | null>(null)

const settingsFetcher = async () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null
  if (!token) return null
  const response = await getUserSettings()
  return response.data
}

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const { data: settings = null, isLoading, mutate } = useSWR<UserSettings | null>(
    'globalSettings',
    settingsFetcher,
    { revalidateOnFocus: false }
  )

  const handleUpdate = async (updates: Partial<Omit<UserSettings, 'id' | 'userId'>>) => {
    const response = await updateUserSettings(updates)
    if (response.success) {
      await mutate()
    }
  }

  return (
    <SettingsContext.Provider
      value={{
        settings,
        isLoading,
        updateSettings: handleUpdate,
        mutateSettings: () => { mutate() },
      }}
    >
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}
