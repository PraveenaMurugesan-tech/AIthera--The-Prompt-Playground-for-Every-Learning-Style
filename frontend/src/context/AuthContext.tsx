import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchCurrentUser, loginUser, logoutUser, registerUser } from '../services/api'

type User = {
  id: number
  email: string
  name?: string
}

type LoginRequest = {
  email: string
  password: string
  rememberMe?: boolean
}

type RegisterRequest = {
  name: string
  email: string
  password: string
}

type AuthContextValue = {
  currentUser: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  login: (credentials: LoginRequest) => Promise<void>
  register: (payload: RegisterRequest) => Promise<void>
  logout: () => Promise<void>
  getCurrentUser: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const getStoredToken = () => {
  if (typeof window === 'undefined') {
    return null
  }

  return window.localStorage.getItem('auth_token')
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => setError(null)

  const getCurrentUser = async () => {
    const token = getStoredToken()

    if (!token) {
      setCurrentUser(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      const user = await fetchCurrentUser()
      setCurrentUser(user)
      setError(null)
    } catch (requestError) {
      setCurrentUser(null)
      window.localStorage.removeItem('auth_token')
      setError(requestError instanceof Error ? requestError.message : 'Session expired. Please sign in again.')
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials: LoginRequest) => {
    setLoading(true)
    setError(null)

    try {
      const response = await loginUser(credentials.email, credentials.password)
      window.localStorage.setItem('auth_token', response.access_token)
      const user = await fetchCurrentUser()
      setCurrentUser(user)
    } catch (requestError) {
      setCurrentUser(null)
      window.localStorage.removeItem('auth_token')
      setError(requestError instanceof Error ? requestError.message : 'Invalid credentials or network error.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }

  const register = async (payload: RegisterRequest) => {
    setLoading(true)
    setError(null)

    try {
      await registerUser(payload)
    } catch (requestError) {
      throw requestError
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await logoutUser()
    } catch {
      // Keep the UI responsive even if logout request fails.
    } finally {
      window.localStorage.removeItem('auth_token')
      setCurrentUser(null)
      setError(null)
    }
  }

  useEffect(() => {
    void getCurrentUser()
    
    // Listen for unauthorized events from api.ts interceptor
    const handleUnauthorized = () => {
      setCurrentUser(null)
      window.localStorage.removeItem('auth_token')
    }
    
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const value = useMemo(
    () => ({
      currentUser,
      isAuthenticated: Boolean(currentUser),
      loading,
      error,
      login,
      register,
      logout,
      getCurrentUser,
      clearError,
    }),
    [currentUser, loading, error],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
