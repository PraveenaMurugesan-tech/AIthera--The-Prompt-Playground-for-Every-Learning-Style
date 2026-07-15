export interface HistoryItem {
  id: string;
  topic: string;
  learningStyle: string;
  difficulty: string;
  prompt: string;
  createdAt: string;
  isFavorite: boolean;
}

const mockHistory: HistoryItem[] = [
  {
    id: '1',
    topic: 'React Hooks',
    learningStyle: 'Visual',
    difficulty: 'Beginner',
    prompt: 'Explain React Hooks visually for a beginner...',
    createdAt: new Date().toISOString(), // Today
    isFavorite: true,
  },
  {
    id: '2',
    topic: 'Docker Containers',
    learningStyle: 'Kinesthetic',
    difficulty: 'Intermediate',
    prompt: 'Provide a hands-on exercise to learn Docker...',
    createdAt: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    isFavorite: false,
  },
  {
    id: '3',
    topic: 'Machine Learning Basics',
    learningStyle: 'Auditory',
    difficulty: 'Advanced',
    prompt: 'Explain ML concepts as a conversational podcast...',
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(), // Last week
    isFavorite: true,
  },
  {
    id: '4',
    topic: 'TypeScript Generics',
    learningStyle: 'Logical',
    difficulty: 'Advanced',
    prompt: 'Break down TS generics using mathematical logic...',
    createdAt: new Date(Date.now() - 86400000 * 10).toISOString(), // Older
    isFavorite: false,
  }
];

export const historyService = {
  getHistory: async (): Promise<HistoryItem[]> => {
    await new Promise(resolve => setTimeout(resolve, 800));
    return [...mockHistory];
  },
  
  toggleFavorite: async (id: string, isFavorite: boolean): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const item = mockHistory.find(i => i.id === id);
    if (item) item.isFavorite = isFavorite;
  },

  deleteHistoryItem: async (id: string): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const index = mockHistory.findIndex(i => i.id === id);
    if (index > -1) mockHistory.splice(index, 1);
  }
};
