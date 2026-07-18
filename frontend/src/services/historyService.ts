import api from './api';

export interface HistoryItem {
  id: string;
  topic: string;
  learningStyle: string;
  difficulty: string;
  prompt: string;
  createdAt: string;
  isFavorite: boolean;
}

interface BackendPromptResponse {
  id: number;
  user_id: number;
  topic: string;
  learning_style: string;
  difficulty: string;
  generated_prompt: string | null;
  created_at: string;
}

export const historyService = {
  getHistory: async (): Promise<HistoryItem[]> => {
    try {
      const response = await api.get<BackendPromptResponse[]>('/prompts/');
      return response.data.map(item => ({
        id: String(item.id),
        topic: item.topic,
        learningStyle: item.learning_style,
        difficulty: item.difficulty,
        prompt: item.generated_prompt || 'No prompt generated.',
        createdAt: item.created_at.endsWith('Z') ? item.created_at : `${item.created_at}Z`,
        isFavorite: false, // Not supported by backend yet
      }));
    } catch (error) {
      console.error('Failed to fetch history:', error);
      throw error;
    }
  },
  
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  toggleFavorite: async (_unused1: string, _unused2: boolean): Promise<void> => {
    // Backend doesn't support favorites yet, simulate success
    await new Promise(resolve => setTimeout(resolve, 300));
    console.warn('Favorite toggle not supported by backend.');
  },

  deleteHistoryItem: async (id: string): Promise<void> => {
    try {
      await api.delete(`/prompts/${id}`);
    } catch (error) {
      console.error(`Failed to delete history item ${id}:`, error);
      throw error;
    }
  },

  clearHistory: async (): Promise<void> => {
    try {
      await api.delete('/prompts/');
    } catch (error) {
      console.error('Failed to clear history:', error);
      throw error;
    }
  }
};
