import React from 'react';

interface BloomLevelSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export const BloomLevelSelect: React.FC<BloomLevelSelectProps> = ({ value, onChange }) => {
  const levels = [
    { id: 'remember', label: 'Remember', color: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800/50' },
    { id: 'understand', label: 'Understand', color: 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-900/20 dark:text-orange-400 dark:border-orange-800/50' },
    { id: 'apply', label: 'Apply', color: 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800/50' },
    { id: 'analyze', label: 'Analyze', color: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800/50' },
    { id: 'evaluate', label: 'Evaluate', color: 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400 dark:border-blue-800/50' },
    { id: 'create', label: 'Create', color: 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-900/20 dark:text-purple-400 dark:border-purple-800/50' },
  ];

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Bloom's Taxonomy
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {levels.map((level) => (
          <button
            key={level.id}
            type="button"
            onClick={() => onChange(level.id)}
            className={`py-2 px-3 rounded-lg border text-sm font-medium transition-all duration-200 flex items-center justify-center ${
              value === level.id
                ? `${level.color} shadow-sm ring-2 ring-offset-1 ring-blue-500 dark:ring-offset-slate-900`
                : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600'
            }`}
          >
            {level.label}
          </button>
        ))}
      </div>
    </div>
  );
};
