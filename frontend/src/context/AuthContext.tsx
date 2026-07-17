import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type RegisterRequest,
  type User,
} from '../services/api'

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

    console.log('===========================')
    console.log('GET CURRENT USER')
    console.log('Stored Token:', activeToken)

    if (!activeToken) {
      console.log('No token found')
      setCurrentUser(null)
      setToken(null)
      setLoading(false)
      return
    }

    try {
      setLoading(true)

      console.log('Calling fetchCurrentUser...')

      const user = await fetchCurrentUser(activeToken)

      console.log('User fetched successfully:', user)

      setCurrentUser(user)
      setToken(activeToken)
      setError(null)
    } catch (requestError) {
      console.error('GET CURRENT USER FAILED:', requestError)

      setCurrentUser(null)
      setToken(null)
      window.localStorage.removeItem('auth_token')

      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Your session has expired. Please sign in again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials: LoginRequest) => {
    setLoading(true)
    setError(null)

    try {
      console.log('===========================')
      console.log('STEP 1 - Calling loginUser')

      const response = await loginUser(
        credentials.email,
        credentials.password,
      )

      console.log('STEP 2 - Login response:')
      console.log(response)

      const nextToken = response.access_token

      console.log('STEP 3 - Token received:')
      console.log(nextToken)

      window.localStorage.setItem('auth_token', nextToken)
      setToken(nextToken)

      console.log('STEP 4 - Calling fetchCurrentUser')

      const user = await fetchCurrentUser(nextToken)

      console.log('STEP 5 - User received:')
      console.log(user)

      setCurrentUser(user)
      setError(null)

      console.log('STEP 6 - Login completed successfully')
    } catch (requestError) {
      console.error('LOGIN FAILED:')
      console.error(requestError)

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
      console.log('Registering user...')
      await registerUser(payload)
      console.log('Registration successful')
    } catch (requestError) {
      console.error('Registration failed:', requestError)
      throw requestError
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await logoutUser()
    } catch {
      // Ignore logout failures
    } finally {
      console.log('Logging out')

      window.localStorage.removeItem('auth_token')
      setCurrentUser(null)
      setToken(null)
      setError(null)
    }
  }

  useEffect(() => {
    console.log('AuthProvider mounted')
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

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}