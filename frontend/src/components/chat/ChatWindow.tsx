import React, { useRef, useEffect } from 'react';
import { ChatBubble } from './ChatBubble';
import { EmptyConversation } from './EmptyConversation';
import { TypingAnimation } from './TypingAnimation';
import type { ChatMessage } from '../../services/chatService';

interface ChatWindowProps {
  messages: ChatMessage[];
  isTyping: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isTyping }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return <EmptyConversation />;
  }

  return (
    <div className="flex-1 overflow-y-auto w-full scroll-smooth">
      <div className="max-w-4xl mx-auto w-full flex flex-col pb-4">
        {messages.map((message) => (
          <ChatBubble key={message.id} message={message} />
        ))}
        {isTyping && (
          <div className="flex gap-4 p-4 md:p-6 w-full bg-slate-50 dark:bg-slate-800/50">
            <div className="flex-shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <div className="w-5 h-5 flex items-center justify-center">
                <div className="w-2 h-2 bg-current rounded-full animate-ping"></div>
              </div>
            </div>
            <div className="flex-1 min-w-0 flex items-center">
              <TypingAnimation />
            </div>
          </div>
        )}
        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
};
