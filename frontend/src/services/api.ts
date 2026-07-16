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
  payload: LearningPromptRequest,
  token?: string,
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
        timeout: 180,
      },
    }, {
      headers: getAuthHeaders(token),
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

export type PromptHistoryItem = {
  id: number
  user_id: number
  topic: string
  learning_style: string
  difficulty: string
  generated_prompt: string | null
  created_at: string
}

// Fetch full prompt history from backend API, with fallback to local mock data
export const fetchPromptHistory = async (token: string): Promise<PromptHistoryItem[]> => {
  try {
    const response = await api.get<PromptHistoryItem[]>('/prompts/', {
      headers: {
        Authorization: token ? `Bearer ${token}` : undefined,
      },
    })
    return response.data
  } catch (error) {
    console.warn('FastAPI prompt history API is not available, falling back to local storage mock history:', error)
    
    // Fetch mock history from localStorage
    const saved = localStorage.getItem('aithera_prompt_history')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        // Fall back to empty
      }
    }
    
    // Return default seeded mock database history
    const initialMockHistory: PromptHistoryItem[] = [
      {
        id: 101,
        user_id: 1,
        topic: 'React lifecycle hooks and useEffect dependencies',
        learning_style: 'visual',
        difficulty: 'intermediate',
        generated_prompt: '### 👁️ React Hooks Diagram\n\n1. **Mounting**: Runs the body and schedules the effect.\n2. **Updating**: Compares dependencies list. Re-runs if they change.\n3. **Unmounting**: Executes the return cleanup function.\n\n```typescript\nuseEffect(() => {\n  console.log("Mount effect");\n  return () => console.log("Cleanup effect");\n}, [dependencies]);\n```',
        created_at: new Date(Date.now() - 4 * 3600000).toISOString()
      },
      {
        id: 102,
        user_id: 1,
        topic: 'Python Decorators implementation guidelines',
        learning_style: 'step_by_step',
        difficulty: 'advanced',
        generated_prompt: '### 🪜 Step-by-Step Python Decorators\n\n```python\ndef my_decorator(func):\n    def wrapper(*args, **kwargs):\n        print("Before execution")\n        result = func(*args, **kwargs)\n        print("After execution")\n        return result\n    return wrapper\n\n@my_decorator\ndef greet(name):\n    return f"Hello {name}"\n```',
        created_at: new Date(Date.now() - 24 * 3600000).toISOString()
      },
      {
        id: 103,
        user_id: 1,
        topic: 'Introduction to Relational Databases and Primary Keys',
        learning_style: 'conversational',
        difficulty: 'beginner',
        generated_prompt: '### 💬 Databases Analogy\n\nThink of a database like a huge digital school ledger. Each student needs a unique Student ID so they do not get mixed up. In database terms, this is called a **Primary Key**.',
        created_at: new Date(Date.now() - 48 * 3600000).toISOString()
      }
    ]
    localStorage.setItem('aithera_prompt_history', JSON.stringify(initialMockHistory))
    return initialMockHistory
  }
}

// Delete prompt request item from history backend, with local cache cleanup
export const deletePromptFromHistory = async (id: number, token: string): Promise<void> => {
  try {
    await api.delete(`/prompts/${id}`, {
      headers: {
        Authorization: token ? `Bearer ${token}` : undefined,
      },
    })
  } catch (error) {
    console.warn('FastAPI prompt deletion failed, cleaning up local storage mock copy:', error)
  }
  
  // Clean up local storage list
  const saved = localStorage.getItem('aithera_prompt_history')
  if (saved) {
    try {
      const parsed = JSON.parse(saved) as PromptHistoryItem[]
      const updated = parsed.filter(item => item.id !== id)
      localStorage.setItem('aithera_prompt_history', JSON.stringify(updated))
    } catch {
      // Ignored
    }
  }
}

export default api
