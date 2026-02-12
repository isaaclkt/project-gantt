'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { apiFetch, ApiError, ERROR_CODES, getErrorMessage } from '@/lib/api-config'
import { useToast } from '@/components/ui/toast'

interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'manager' | 'member' | 'viewer'
  department?: string
  avatar?: string
}

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const { toast } = useToast()

  const showError = useCallback((message: string) => {
    toast({
      title: 'Erro',
      description: message,
      variant: 'destructive',
    })
  }, [toast])

  const showSuccess = useCallback((message: string) => {
    toast({
      title: 'Sucesso',
      description: message,
      variant: 'success',
    })
  }, [toast])

  // Check if user is authenticated on mount
  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('accessToken')
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      const response = await apiFetch<{ data: User }>('/user/profile')
      setUser(response.data)
    } catch (error) {
      // Token is invalid or expired
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await apiFetch<{
        data: {
          accessToken: string
          refreshToken: string
          user: User
        }
      }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })

      localStorage.setItem('accessToken', response.data.accessToken)
      localStorage.setItem('refreshToken', response.data.refreshToken)
      setUser(response.data.user)
      showSuccess('Login realizado com sucesso!')
      return true
    } catch (error) {
      if (error instanceof ApiError) {
        showError(getErrorMessage(error))
      } else {
        showError('Erro ao fazer login')
      }
      return false
    }
  }

  const logout = async (): Promise<void> => {
    try {
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        await apiFetch('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
      }
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      setUser(null)
      router.push('/login')
    }
  }

  const refreshUser = async (): Promise<void> => {
    try {
      const response = await apiFetch<{ data: User }>('/user/profile')
      setUser(response.data)
    } catch (error) {
      // If refresh fails, log out
      await logout()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// HOC for protected routes
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: { requiredRole?: string[] } = {}
) {
  return function ProtectedRoute(props: P) {
    const { user, isLoading, isAuthenticated } = useAuth()
    const router = useRouter()
    const { toast } = useToast()

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/login')
      }
    }, [isLoading, isAuthenticated, router])

    useEffect(() => {
      if (user && options.requiredRole && !options.requiredRole.includes(user.role)) {
        toast({
          title: 'Acesso Negado',
          description: 'Você não tem permissão para acessar esta página.',
          variant: 'destructive',
        })
        router.push('/')
      }
    }, [user, router, toast])

    if (isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      return null
    }

    if (options.requiredRole && user && !options.requiredRole.includes(user.role)) {
      return null
    }

    return <Component {...props} />
  }
}
