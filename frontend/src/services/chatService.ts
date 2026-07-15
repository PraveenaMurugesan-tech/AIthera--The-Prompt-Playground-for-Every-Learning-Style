export type MessageRole = 'user' | 'ai';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  senderName?: string; // e.g. "AI Council"
}

export const chatService = {
  getInitialMessages: (): ChatMessage[] => {
    return [
      {
        id: '1',
        role: 'user',
        content: 'I want to learn about React Context API. I am a visual learner.',
        timestamp: new Date(Date.now() - 60000).toISOString(),
      },
      {
        id: '2',
        role: 'ai',
        content: 'I can help with that! Here is a visual breakdown of how the React Context API works:\\n\\n1. **Provider**: Think of this as a global broadcasting tower.\\n2. **Consumer**: These are the radios tuning into the broadcast.\\n\\nWould you like me to generate a tailored prompt to dive deeper into this?',
        timestamp: new Date(Date.now() - 50000).toISOString(),
        senderName: 'AI Council',
      },
    ];
  },

  sendMessage: async (content: string, _history: ChatMessage[]): Promise<ChatMessage> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      id: Math.random().toString(36).substr(2, 9),
      role: 'ai',
      content: `I've received your message: "${content}". This is a mock response from the AIthera Council. We're currently simulating the conversation flow.`,
      timestamp: new Date().toISOString(),
      senderName: 'AI Council',
    };
  }
};
