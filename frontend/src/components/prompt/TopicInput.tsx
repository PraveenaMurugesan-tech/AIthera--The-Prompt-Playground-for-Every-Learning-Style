import React from 'react';
import { BookOpen } from 'lucide-react';

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
}

export const TopicInput: React.FC<TopicInputProps> = ({ value, onChange }) => {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="topic" className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Topic
      </label>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <BookOpen className="h-5 w-5 text-slate-400" />
        </div>
        <input
          type="text"
          id="topic"
          className="block w-full pl-10 pr-3 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white transition-shadow shadow-sm"
          placeholder="Example: Explain Neural Networks"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    </div>
  );
};
