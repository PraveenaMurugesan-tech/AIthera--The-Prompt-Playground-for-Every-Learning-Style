import axios, { AxiosError } from 'axios'

export type RegisterRequest = {
  name: string
  email: string
  password: string
}

export type AuthResponse = {
  access_token: string
  token_type: string
}

export type User = {
  id: number
  email: string
  name?: string
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

const getAuthHeaders = (token?: string) => ({
  Authorization: token ? `Bearer ${token}` : undefined,
})

const extractErrorMessage = (payload: unknown): string | null => {
  if (typeof payload === 'string') {
    return payload
  }

  if (payload && typeof payload === 'object') {
    const record = payload as Record<string, unknown>

    if (typeof record.detail === 'string') {
      return record.detail
    }

    if (typeof record.message === 'string') {
      return record.message
    }

    if (typeof record.error === 'string') {
      return record.error
    }

    if (Array.isArray(record.errors)) {
      return record.errors.map((item) => (typeof item === 'string' ? item : '')).filter(Boolean).join(' ')
    }
  }

  return null
}

const normalizeError = (error: unknown) => {
  if (error instanceof AxiosError) {
    const message = extractErrorMessage(error.response?.data) ?? error.message
    const lowerMessage = message.toLowerCase()

    if (error.code === 'ERR_NETWORK' || error.message.toLowerCase().includes('network') || error.code === 'ECONNABORTED' || error.message.toLowerCase().includes('timeout')) {
      return 'The server is unavailable right now. Please try again in a moment.'
    }

    if (error.response?.status === 401) {
      if (lowerMessage.includes('credential') || lowerMessage.includes('invalid') || lowerMessage.includes('password')) {
        return 'Invalid credentials. Please check your email and password.'
      }
      return 'Your session has expired. Please sign in again.'
    }

    if (error.response?.status === 403) {
      return 'You do not have permission to perform this action.'
    }

    if (error.response?.status === 400 || error.response?.status === 409) {
      if (lowerMessage.includes('already') && lowerMessage.includes('exist')) {
        return 'An account with this email already exists.'
      }
      if (lowerMessage.includes('email')) {
        return 'Please use a valid email address.'
      }
      if (lowerMessage.includes('password')) {
        return 'Please choose a stronger password with at least 8 characters.'
      }
      return 'Please review your information and try again.'
    }

    if (error.response?.status && error.response.status >= 500) {
      return 'The server is unavailable right now. Please try again later.'
    }

    return typeof message === 'string' && message ? message : 'Unexpected server error.'
  }

  return 'Unexpected server error.'
}

export const loginUser = async (email: string, password: string): Promise<AuthResponse> => {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)

  try {
    const response = await api.post<AuthResponse>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export const registerUser = async (payload: RegisterRequest): Promise<User> => {
  try {
    const response = await api.post<User>('/auth/register', payload)
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export const fetchCurrentUser = async (token: string): Promise<User> => {
  try {
    const response = await api.get<User>('/auth/me', {
      headers: getAuthHeaders(token),
    })
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export const logoutUser = async (): Promise<void> => {
  await Promise.resolve()
}

export default api
