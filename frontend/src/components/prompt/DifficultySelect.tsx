import React from 'react';

interface DifficultySelectProps {
  value: string;
  onChange: (value: string) => void;
}

export const DifficultySelect: React.FC<DifficultySelectProps> = ({ value, onChange }) => {
  const difficulties = [
    { id: 'beginner', label: 'Beginner' },
    { id: 'intermediate', label: 'Intermediate' },
    { id: 'advanced', label: 'Advanced' },
  ];

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="difficulty" className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Difficulty
      </label>
      <div className="flex gap-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
        {difficulties.map((diff) => (
          <button
            key={diff.id}
            type="button"
            onClick={() => onChange(diff.id)}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all duration-200 ${
              value === diff.id
                ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50'
            }`}
          >
            {diff.label}
          </button>
        ))}
      </div>
    </div>
  );
};
