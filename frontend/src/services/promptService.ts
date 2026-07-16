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

const mockProviders: ProviderState[] = [
  { id: 'claude', name: 'Claude', status: 'Waiting' },
  { id: 'gemini', name: 'Gemini', status: 'Waiting' },
  { id: 'deepseek', name: 'DeepSeek', status: 'Waiting' },
  { id: 'groq', name: 'Groq', status: 'Waiting' },
  { id: 'cerebras', name: 'Cerebras', status: 'Waiting' },
  { id: 'sambanova', name: 'SambaNova', status: 'Waiting' },
  { id: 'openrouter', name: 'OpenRouter', status: 'Waiting' },
];

export const promptService = {
  getInitialProviders: (): ProviderState[] => {
    return [...mockProviders];
  },

  generatePrompt: async (data: any): Promise<GenerationResult> => {
    try {
      const payload = {
        topic: data.topic,
        learning_style: data.learningStyle,
        difficulty: data.difficulty,
        bloom_level: data.bloomLevel || 'understand',
        options: data.instructions ? { instructions: data.instructions } : {}
      };

      console.log('Sending prompt generation request with payload:', JSON.stringify(payload, null, 2));

      const response = await api.post('/prompts/generate', payload);
      const backendData = response.data;

      return {
        optimizedPrompt: backendData.optimized_prompt || 'No prompt generated.',
        consensusSummary: backendData.consensus_reasoning || 'No consensus reasoning provided.',
        confidenceScore: backendData.confidence_score || 0,
        agreementScore: backendData.agreement_score || 0,
        educationalMetrics: {
          difficulty: backendData.educational_metrics?.difficulty || data.difficulty,
          bloomLevel: backendData.educational_metrics?.bloomLevel || data.bloomLevel,
          learningStyle: backendData.educational_metrics?.learningStyle || data.learningStyle,
          estimatedStudyTime: backendData.educational_metrics?.estimatedStudyTime || '30 mins',
          complexity: backendData.educational_metrics?.complexity || 'Medium',
        },
        recommendations: {
          followUpTopics: backendData.recommendations?.filter((r: any) => r.category === 'Topics' || r.category === 'Follow Up').map((r: any) => r.suggestion) || [],
          learningPath: backendData.learning_path?.steps?.map((s: any) => s.title) || [],
          practiceSuggestions: backendData.recommendations?.filter((r: any) => r.category !== 'Topics' && r.category !== 'Follow Up').map((r: any) => r.suggestion) || [],
        },
        variants: backendData.prompt_variants?.map((v: any) => ({
          id: v.style || Math.random().toString(),
          name: v.title,
          content: v.prompt_text,
        })) || []
      };
    } catch (error) {
      console.error('Error generating prompt:', error);
      throw error;
    }
  },

  getPromptResult: async (_jobId: string, formData: any = {}): Promise<GenerationResult> => {
    // Left for backward compatibility if any old components call it, 
    // but the main flow now just uses the synchronous return of generatePrompt.
    return promptService.generatePrompt(formData);
  }
};
