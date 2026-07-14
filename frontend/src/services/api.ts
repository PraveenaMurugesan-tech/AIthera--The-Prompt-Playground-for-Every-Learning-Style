import axios, { AxiosError } from 'axios'

type RegisterRequest = {
  name: string
  email: string
  password: string
}

type AuthResponse = {
  access_token: string
  token_type: string
}

type User = {
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

const normalizeError = (error: unknown) => {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.detail || error.message
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return 'The request timed out. Please try again.'
    }
    if (error.response?.status === 401) {
      return 'Your session has expired. Please sign in again.'
    }
    if (error.response?.status === 403) {
      return 'You do not have permission to perform this action.'
    }
    return typeof message === 'string' ? message : 'Unexpected server error.'
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
