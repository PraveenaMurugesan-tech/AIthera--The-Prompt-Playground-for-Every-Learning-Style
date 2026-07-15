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
  { id: 'gpt', name: 'GPT', status: 'Waiting' },
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

  generatePrompt: async (data: any): Promise<{ jobId: string }> => {
    // Simulate initiating a generation job
    console.log('Initiating prompt generation with data:', data);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ jobId: 'mock-job-123' });
      }, 500);
    });
  },

  getPromptResult: async (jobId: string): Promise<GenerationResult> => {
    console.log('Fetching result for job:', jobId);
    // Simulate fetching the final result
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          optimizedPrompt: "Act as an expert computer science tutor specializing in visual learning. Explain the concept of [Topic] using clear analogies, diagrams described in text, and real-world examples. Ensure the difficulty is tailored to a [Difficulty] level and targets the [Bloom Level] level of understanding. Please follow these additional instructions: [Instructions].",
          consensusSummary: "The AI Council agreed that a visual approach with concrete analogies best suits your learning style. GPT provided the structure, Claude refined the analogies, and Gemini ensured the Bloom's taxonomy level was perfectly targeted.",
          confidenceScore: 94,
          agreementScore: 91,
          educationalMetrics: {
            difficulty: 'Intermediate',
            bloomLevel: 'Application',
            learningStyle: 'Visual',
            estimatedStudyTime: '45 mins',
            complexity: 'Medium',
          },
          recommendations: {
            followUpTopics: ['Advanced Data Structures', 'Algorithmic Complexity', 'System Design Basics'],
            learningPath: ['Understand the core concept', 'Analyze real-world examples', 'Implement a basic version'],
            practiceSuggestions: ['Draw a diagram of the process', 'Explain it to a peer', 'Write a short summary'],
          },
          variants: [
            {
              id: 'v1',
              name: 'Socratic Method',
              content: 'Act as a Socratic tutor. Guide me to understand [Topic] by asking probing questions...'
            },
            {
              id: 'v2',
              name: 'Direct Instruction',
              content: 'Provide a clear, step-by-step explanation of [Topic] focusing on the core principles...'
            }
          ]
        });
      }, 1000);
    });
  }
};
