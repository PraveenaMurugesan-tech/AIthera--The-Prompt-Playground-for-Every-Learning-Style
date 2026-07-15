import React from 'react';
import { History } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const EmptyHistory: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
        <History className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
        No prompt history yet
      </h3>
      <p className="text-slate-500 dark:text-slate-400 max-w-md mb-6">
        When you generate personalized learning prompts, they will appear here for easy access and organization.
      </p>
      <button
        onClick={() => navigate('/prompt')}
        className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-sm"
      >
        Generate Your First Prompt
      </button>
    </div>
  );
};
