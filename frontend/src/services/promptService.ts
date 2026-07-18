import api from './api';

export type ProviderStatus = 'Waiting' | 'Processing' | 'Completed' | 'Failed';

export interface ProviderState {
  id: string;
  name: string;
  status: ProviderStatus;
}

export interface GenerationResult {
  optimizedPrompt: string;
  consensusSummary: string;
  confidenceScore: number;
  agreementScore: number;
  educationalMetrics: {
    difficulty: string;
    bloomLevel: string;
    learningStyle: string;
    estimatedStudyTime: string;
    complexity: string;
  };
  recommendations: {
    followUpTopics: string[];
    learningPath: string[];
    practiceSuggestions: string[];
  };
  variants: {
    id: string;
    name: string;
    content: string;
  }[];
}

export interface PromptRequestData {
  topic: string;
  learningStyle: string;
  difficulty: string;
  bloomLevel?: string;
  instructions?: string;
}

export interface BackendRecommendation {
  category: string;
  suggestion: string;
}

export interface BackendLearningPathStep {
  title: string;
  description?: string;
}

export interface BackendPromptVariant {
  style?: string;
  title: string;
  prompt_text: string;
}

export interface BackendEducationalMetrics {
  difficulty?: string;
  bloomLevel?: string;
  learningStyle?: string;
  estimatedStudyTime?: string;
  complexity?: string;
}

export interface BackendGenerationResponse {
  optimized_prompt?: string;
  consensus_reasoning?: string;
  confidence_score?: number;
  agreement_score?: number;
  educational_metrics?: BackendEducationalMetrics;
  recommendations?: BackendRecommendation[];
  learning_path?: { steps?: BackendLearningPathStep[] };
  prompt_variants?: BackendPromptVariant[];
}

const mockProviders: ProviderState[] = [
  { id: 'claude', name: 'Claude', status: 'Waiting' },
  { id: 'gemini', name: 'Gemini', status: 'Waiting' },
  { id: 'deepseek', name: 'DeepSeek', status: 'Waiting' },
  { id: 'groq', name: 'Groq', status: 'Waiting' },
  { id: 'cerebras', name: 'Cerebras', status: 'Waiting' },
  { id: 'sambanova', name: 'SambaNova', status: 'Waiting' },
  { id: 'openrouter', name: 'OpenRouter', status: 'Waiting' },
];

let currentGenerationPromise: Promise<GenerationResult> | null = null;
let currentGenerationPayload: string | null = null;

export const promptService = {
  getInitialProviders: (): ProviderState[] => {
    return [...mockProviders];
  },

  generatePrompt: async (data: PromptRequestData): Promise<GenerationResult> => {
    const payload = {
      topic: data.topic,
      learning_style: data.learningStyle,
      difficulty: data.difficulty,
      bloom_level: data.bloomLevel || 'understand',
      options: data.instructions ? { instructions: data.instructions } : {}
    };

    const payloadStr = JSON.stringify(payload);
    if (currentGenerationPromise && currentGenerationPayload === payloadStr) {
      return currentGenerationPromise;
    }

    currentGenerationPayload = payloadStr;
    currentGenerationPromise = (async () => {
      try {
        const response = await api.post<BackendGenerationResponse>('/prompts/generate', payload);
        const backendData = response.data;

        return {
          optimizedPrompt: backendData.optimized_prompt || 'No prompt generated.',
          consensusSummary: backendData.consensus_reasoning || 'No consensus reasoning provided.',
          confidenceScore: backendData.confidence_score || 0,
          agreementScore: backendData.agreement_score || 0,
          educationalMetrics: {
            difficulty: backendData.educational_metrics?.difficulty || data.difficulty,
            bloomLevel: backendData.educational_metrics?.bloomLevel || (data.bloomLevel || 'understand'),
            learningStyle: backendData.educational_metrics?.learningStyle || data.learningStyle,
            estimatedStudyTime: backendData.educational_metrics?.estimatedStudyTime || '30 mins',
            complexity: backendData.educational_metrics?.complexity || 'Medium',
          },
          recommendations: {
            followUpTopics: backendData.recommendations?.filter(r => r.category === 'Topics' || r.category === 'Follow Up').map(r => r.suggestion) || [],
            learningPath: backendData.learning_path?.steps?.map(s => s.title) || [],
            practiceSuggestions: backendData.recommendations?.filter(r => r.category !== 'Topics' && r.category !== 'Follow Up').map(r => r.suggestion) || [],
          },
          variants: backendData.prompt_variants?.map(v => ({
            id: v.style || Math.random().toString(),
            name: v.title,
            content: v.prompt_text,
          })) || []
        };
      } finally {
        if (currentGenerationPayload === payloadStr) {
          currentGenerationPromise = null;
          currentGenerationPayload = null;
        }
      }
    })();

    return currentGenerationPromise;
  },

  getPromptResult: async (_jobId: string, formData: Partial<PromptRequestData> = {}): Promise<GenerationResult> => {
    // Left for backward compatibility if any old components call it, 
    // but the main flow now just uses the synchronous return of generatePrompt.
    return promptService.generatePrompt(formData as PromptRequestData);
  }
};
