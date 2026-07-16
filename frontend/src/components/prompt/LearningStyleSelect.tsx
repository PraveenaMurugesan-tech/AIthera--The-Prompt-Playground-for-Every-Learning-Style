import React from 'react';
import { Palette, Headphones, Book, Brain, Activity } from 'lucide-react';

interface LearningStyleSelectProps {
  value: string;
  onChange: (value: string) => void;
}

export const LearningStyleSelect: React.FC<LearningStyleSelectProps> = ({ value, onChange }) => {
  const styles = [
    { id: 'visual', label: 'Visual', icon: Palette },
    { id: 'conversational', label: 'Conversational', icon: Headphones },
    { id: 'step_by_step', label: 'Step-by-Step', icon: Book },
    { id: 'exam_focused', label: 'Exam-Focused', icon: Brain },
    { id: 'research_oriented', label: 'Research-Oriented', icon: Activity },
  ];

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="learningStyle" className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Learning Style
      </label>
      <div className="relative">
        <select
          id="learningStyle"
          className="block w-full pl-3 pr-10 py-3 text-base border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-slate-800 dark:border-slate-700 dark:text-white transition-shadow shadow-sm appearance-none"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="" disabled>Select a learning style</option>
          {styles.map((style) => (
            <option key={style.id} value={style.id}>
              {style.label}
            </option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500">
          <svg className="h-4 w-4 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
          </svg>
        </div>
      </div>
    </div>
  );
};
