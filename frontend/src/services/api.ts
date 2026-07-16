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
  timeout: 300000, // 5 minutes timeout
})

// Request Interceptor: Attach JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Centralized error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      // Dispatch custom event to trigger logout in AuthContext
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);

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

export const analyzeImage = async (file: File): Promise<{ topic: string, instructions: string }> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/prompts/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export const fetchCurrentUser = async (): Promise<User> => {
  try {
    // Interceptor will attach token
    const response = await api.get<User>('/auth/me')
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export const logoutUser = async (): Promise<void> => {
  localStorage.removeItem('auth_token');
  await Promise.resolve()
}

export default api
