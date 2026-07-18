import React from 'react';
import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';
import { MessageToolbar } from './MessageToolbar';
import type { ChatMessage } from '../../services/chatService';

interface ChatBubbleProps {
  message: ChatMessage;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 p-4 md:p-6 w-full ${isUser ? '' : 'bg-slate-50 dark:bg-slate-800/50'} group`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center
        ${isUser 
          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' 
          : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-slate-900 dark:text-white">
            {isUser ? 'You' : message.senderName || 'AI'}
          </span>
          <span className="text-xs text-slate-400">
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        
        <div className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
          {message.content}
        </div>

        {!isUser && <MessageToolbar text={message.content} />}
      </div>
    </motion.div>
  );
};
