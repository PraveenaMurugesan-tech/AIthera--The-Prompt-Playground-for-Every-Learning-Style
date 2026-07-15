import React from 'react';
import { Network, Sparkles, Zap } from 'lucide-react';

export const EmptyConversation: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 text-center">
      <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center mb-6">
        <Network className="w-8 h-8" />
      </div>
      <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
        Welcome to the AI Council Workspace
      </h2>
      <p className="text-slate-500 dark:text-slate-400 max-w-lg mb-8">
        Interact with multiple AI models simultaneously. Ask a question, and our consensus algorithm will deliver the most optimized response.
      </p>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl w-full">
        <div className="p-4 border border-slate-200 dark:border-slate-800 rounded-xl text-left bg-white dark:bg-slate-900 hover:shadow-md transition-shadow cursor-pointer">
          <Sparkles className="w-5 h-5 text-indigo-500 mb-2" />
          <h4 className="font-semibold text-slate-900 dark:text-white text-sm mb-1">Explain quantum computing</h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">using simple analogies for a beginner.</p>
        </div>
        <div className="p-4 border border-slate-200 dark:border-slate-800 rounded-xl text-left bg-white dark:bg-slate-900 hover:shadow-md transition-shadow cursor-pointer">
          <Zap className="w-5 h-5 text-amber-500 mb-2" />
          <h4 className="font-semibold text-slate-900 dark:text-white text-sm mb-1">Generate a lesson plan</h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">for teaching React Hooks to visual learners.</p>
        </div>
      </div>
    </div>
  );
};
