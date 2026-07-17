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

export type PromptFormat = 'notes' | 'quiz' | 'explanation' | 'flashcards'

export type LearningPromptRequest = {
  topic: string
  learningStyle: 'adaptive' | 'visual' | 'step_by_step' | 'conversational' | 'exam_focused'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  format: PromptFormat
}

export type GeneratedPromptResponse = {
  title: string
  summary: string
  content: string
  badge: string
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || (import.meta.env.PROD ? 'https://api.aithera.com' : 'http://localhost:8000'),
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
      const lowerMessage = typeof dataMessage === 'string' ? dataMessage.toLowerCase() : '';
      if (lowerMessage.includes('credential') || lowerMessage.includes('invalid') || lowerMessage.includes('password') || lowerMessage.includes('incorrect')) {
        errorMessage = 'Invalid credentials. Please check your email and password.';
      } else {
        errorMessage = 'Your session has expired. Please sign in again.';
      }
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

const buildMockPrompt = (payload: LearningPromptRequest): GeneratedPromptResponse => {
  const formatLabel = payload.format.charAt(0).toUpperCase() + payload.format.slice(1)
  const title = `${formatLabel} prompt ready`
  const summary = `A ${payload.difficulty} ${payload.learningStyle.replace(/_/g, ' ')} prompt designed for ${payload.topic}.`
  const content = [
    `Topic: ${payload.topic}`,
    `Learning style: ${payload.learningStyle.replace(/_/g, ' ')}`,
    `Difficulty: ${payload.difficulty}`,
    '',
    '1. Start by defining the core concept in your own words.',
    '2. Add one concrete example that connects the topic to everyday life.',
    '3. Finish with a short reflection on what you learned and what to practice next.',
  ].join('\n')

  return {
    title,
    summary,
    content,
    badge: 'Mock preview',
  }
}

export const generateLearningPrompt = async (
  payload: LearningPromptRequest
): Promise<GeneratedPromptResponse> => {
  try {
    const response = await api.post<{
      optimized_prompt?: string
      consensus_reasoning?: string
      confidence_score?: number
    }>('/prompts/generate', {
      topic: payload.topic,
      learning_style: payload.learningStyle,
      difficulty: payload.difficulty,
      bloom_level: 'understand',
      options: {
        skip_variants: true,
        skip_learning_path: true,
      },
    })

    const optimizedPrompt = response.data.optimized_prompt?.trim()

    if (optimizedPrompt) {
      return {
        title: `${payload.format.charAt(0).toUpperCase() + payload.format.slice(1)} prompt ready`,
        summary: response.data.consensus_reasoning || 'Prompt generated by the AI council.',
        content: optimizedPrompt,
        badge: 'AI generated',
      }
    }
  } catch {
    // TODO: Replace this mock fallback with a real prompt-generation flow once the backend service is stable.
  }

  return buildMockPrompt(payload)
}

export const sendChatMessage = async (messages: { role: string; content: string }[]): Promise<{ content: string }> => {
  try {
    const response = await api.post('/prompts/chat', { messages })
    return response.data
  } catch (error) {
    throw new Error(normalizeError(error), { cause: error })
  }
}

export default api
