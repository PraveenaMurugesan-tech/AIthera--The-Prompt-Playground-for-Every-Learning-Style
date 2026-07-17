import axios, { AxiosError } from 'axios'
import type { AxiosRequestConfig } from 'axios'
import toast from 'react-hot-toast'

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

interface RetryConfig extends AxiosRequestConfig {
  _retryCount?: number;
}

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

// Response Interceptor: Centralized error handling and Retry Mechanism
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryConfig;
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.dispatchEvent(new Event('auth:unauthorized'));
      return Promise.reject(error);
    }

    // Determine if we should retry (Network error, timeout, or 5xx server error)
    const isNetworkError = !error.response;
    const is5xxError = error.response?.status && error.response.status >= 500;
    const isRateLimited = error.response?.status === 429;
    
    if (originalRequest && (isNetworkError || is5xxError || isRateLimited)) {
      originalRequest._retryCount = originalRequest._retryCount || 0;
      
      if (originalRequest._retryCount < MAX_RETRIES) {
        originalRequest._retryCount += 1;
        
        // Exponential backoff
        const delay = isRateLimited 
          ? (parseInt(error.response?.headers['retry-after'] || '1', 10) * 1000)
          : (RETRY_DELAY_MS * Math.pow(2, originalRequest._retryCount - 1));
          
        await new Promise(resolve => setTimeout(resolve, delay));
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

export const normalizeError = (error: unknown, showToast: boolean = false) => {
  let errorMessage = 'Unexpected server error.';

  if (error instanceof AxiosError) {
    const dataMessage = error.response?.data?.detail || error.response?.data?.message || error.message;
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      errorMessage = 'The request timed out. Please try again.';
    } else if (!error.response) {
      errorMessage = 'Network error. Please check your connection.';
    } else if (error.response.status === 400) {
      errorMessage = typeof dataMessage === 'string' ? dataMessage : 'Invalid request.';
    } else if (error.response.status === 401) {
      errorMessage = 'Your session has expired. Please sign in again.';
    } else if (error.response.status === 403) {
      errorMessage = 'You do not have permission to perform this action.';
    } else if (error.response.status === 404) {
      errorMessage = 'Resource not found.';
    } else if (error.response.status === 429) {
      errorMessage = 'Too many requests. Please wait a moment.';
    } else if (error.response.status >= 500) {
      errorMessage = 'Server error. Please try again later.';
    } else {
      errorMessage = typeof dataMessage === 'string' ? dataMessage : errorMessage;
    }
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }

  if (showToast) {
    toast.error(errorMessage);
  }

  return errorMessage;
};

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
    throw new Error(normalizeError(error), { cause: error })
  }
}

export const registerUser = async (payload: RegisterRequest): Promise<User> => {
  try {
    const response = await api.post<User>('/auth/register', payload)
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error), { cause: error })
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
    throw new Error(normalizeError(error, true), { cause: error })
  }
}

export const fetchCurrentUser = async (): Promise<User> => {
  try {
    const response = await api.get<User>('/auth/me')
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error), { cause: error })
  }
}

export const logoutUser = async (): Promise<void> => {
  localStorage.removeItem('auth_token');
  await Promise.resolve()
}

export default api
