import React, { useState, useEffect } from 'react';
import { ChatWindow } from '../../components/chat/ChatWindow';
import { ChatInput } from '../../components/chat/ChatInput';
import { chatService } from '../../services/chatService';
import type { ChatMessage } from '../../services/chatService';

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Load initial mock messages
    setMessages(chatService.getInitialMessages());
  }, []);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await chatService.sendMessage(userMsg.content, messages);
      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-[#F8FAFC] dark:bg-slate-950 relative">
      {/* Messages Area */}
      <ChatWindow messages={messages} isTyping={isTyping} />

      {/* Input Area */}
      <div className="w-full bg-gradient-to-t from-[#F8FAFC] via-[#F8FAFC] to-transparent dark:from-slate-950 dark:via-slate-950 pb-4 pt-8 px-4 md:px-8 shrink-0">
        <div className="max-w-4xl mx-auto w-full">
          <ChatInput 
            value={inputValue}
            onChange={setInputValue}
            onSend={handleSend}
            isLoading={isTyping}
          />
          <p className="text-center text-xs text-slate-400 mt-3">
            AIthera Council can make mistakes. Consider verifying important information.
          </p>
        </div>
      </div>
    </div>
  );
};
