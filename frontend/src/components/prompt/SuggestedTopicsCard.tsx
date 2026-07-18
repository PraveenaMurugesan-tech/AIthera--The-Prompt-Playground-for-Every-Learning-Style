import React from 'react';
import { Lightbulb } from 'lucide-react';

export const SuggestedTopicsCard: React.FC = () => {
  const topics = [
    'Machine Learning',
    'Photosynthesis',
    'Blockchain',
    'Newton\'s Laws',
    'Data Structures',
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <Lightbulb className="h-5 w-5 text-yellow-500" />
        Suggested Topics
      </h3>
      <div className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <button
            key={topic}
            className="px-3 py-1.5 rounded-full text-sm font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 hover:text-slate-900 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 dark:hover:text-white transition-colors"
          >
            {topic}
          </button>
        ))}
      </div>
    </div>
  );
};
