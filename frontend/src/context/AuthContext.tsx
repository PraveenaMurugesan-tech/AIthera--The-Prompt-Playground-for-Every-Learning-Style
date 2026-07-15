import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { fetchCurrentUser, loginUser, logoutUser, registerUser, type RegisterRequest, type User } from '../services/api'

type LoginRequest = {
  email: string
  password: string
  rememberMe?: boolean
}

type AuthContextValue = {
  currentUser: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  token: string | null
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
  const [token, setToken] = useState<string | null>(getStoredToken())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => setError(null)

  const getCurrentUser = async () => {
    const activeToken = getStoredToken()

    if (!activeToken) {
      setCurrentUser(null)
      setToken(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      const user = await fetchCurrentUser(activeToken)
      setCurrentUser(user)
      setToken(activeToken)
      setError(null)
    } catch (requestError) {
      setCurrentUser(null)
      setToken(null)
      window.localStorage.removeItem('auth_token')
      setError(requestError instanceof Error ? requestError.message : 'Your session has expired. Please sign in again.')
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials: LoginRequest) => {
    setLoading(true)
    setError(null)

    try {
      const response = await loginUser(credentials.email, credentials.password)
      const nextToken = response.access_token
      window.localStorage.setItem('auth_token', nextToken)
      setToken(nextToken)
      const user = await fetchCurrentUser(nextToken)
      setCurrentUser(user)
      setError(null)
    } catch (requestError) {
      setCurrentUser(null)
      setToken(null)
      window.localStorage.removeItem('auth_token')
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
      setToken(null)
      setError(null)
    }
  }

  useEffect(() => {
    void getCurrentUser()
  }, [])

  const value = useMemo(
    () => ({
      currentUser,
      isAuthenticated: Boolean(currentUser && token),
      loading,
      error,
      token,
      login,
      register,
      logout,
      getCurrentUser,
      clearError,
    }),
    [currentUser, loading, error, token],
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
