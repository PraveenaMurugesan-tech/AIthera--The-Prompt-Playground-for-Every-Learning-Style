import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export const CouncilStatusCard: React.FC = () => {
  const members = [
    'GPT',
    'Claude',
    'Gemini',
    'DeepSeek',
    'Groq',
    'Cerebras',
    'SambaNova',
    'OpenRouter',
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        AI Council Members
      </h3>
      <div className="flex flex-col gap-3">
        {members.map((member) => (
          <div key={member} className="flex items-center justify-between group">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
              {member}
            </span>
            <div className="flex items-center gap-1.5 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 px-2 py-1 rounded-full text-xs font-medium border border-green-200 dark:border-green-800/50">
              <CheckCircle2 className="h-3 w-3" />
              Ready
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
