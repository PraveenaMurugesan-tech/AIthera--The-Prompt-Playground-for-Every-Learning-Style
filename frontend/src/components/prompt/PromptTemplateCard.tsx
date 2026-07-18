import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';

export const PromptTemplateCard: React.FC = () => {
  const templates = [
    'Learn with Analogies',
    'Visual Explanation',
    'Exam Preparation',
    'Quick Revision',
    'Hands-on Practice',
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Recent Templates
      </h3>
      <div className="flex flex-col gap-2">
        {templates.map((template) => (
          <button
            key={template}
            className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 text-left transition-colors border border-transparent hover:border-slate-200 dark:hover:border-slate-700 group"
          >
            <div className="flex items-center gap-3">
              <div className="bg-blue-50 dark:bg-blue-900/20 p-2 rounded-lg text-blue-600 dark:text-blue-400 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/40 transition-colors">
                <FileText className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {template}
              </span>
            </div>
            <ChevronRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
};
