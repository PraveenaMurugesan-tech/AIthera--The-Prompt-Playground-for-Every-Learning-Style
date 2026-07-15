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

  getPromptResult: async (jobId: string, formData: any = {}): Promise<GenerationResult> => {
    console.log('Fetching result for job:', jobId, 'with data:', formData);
    
    // Default values if formData is empty
    const topic = formData.topic || '[Topic]';
    const difficulty = formData.difficulty || '[Difficulty]';
    const bloomLevel = formData.bloomLevel || '[Bloom Level]';
    const learningStyle = formData.learningStyle || 'visual';
    const instructions = formData.instructions ? ` Please follow these additional instructions: ${formData.instructions}.` : '';

    const optimizedPrompt = `Act as an expert computer science tutor specializing in ${learningStyle} learning. Explain the concept of ${topic} using clear analogies, diagrams described in text, and real-world examples. Ensure the difficulty is tailored to a ${difficulty} level and targets the ${bloomLevel} level of understanding.${instructions}`;

    // Simulate fetching the final result
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          optimizedPrompt,
          consensusSummary: `The AI Council agreed that a ${learningStyle} approach with concrete analogies best suits your learning style. GPT provided the structure, Claude refined the analogies, and Gemini ensured the Bloom's taxonomy level was perfectly targeted for ${topic}.`,
          confidenceScore: 94,
          agreementScore: 91,
          educationalMetrics: {
            difficulty: difficulty !== '[Difficulty]' ? difficulty : 'Intermediate',
            bloomLevel: bloomLevel !== '[Bloom Level]' ? bloomLevel : 'Application',
            learningStyle: learningStyle !== 'visual' ? learningStyle : 'Visual',
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
              content: `Act as a Socratic tutor. Guide me to understand ${topic} by asking probing questions...`
            },
            {
              id: 'v2',
              name: 'Direct Instruction',
              content: `Provide a clear, step-by-step explanation of ${topic} focusing on the core principles...`
            }
          ]
        });
      }, 1000);
    });
  }
};
