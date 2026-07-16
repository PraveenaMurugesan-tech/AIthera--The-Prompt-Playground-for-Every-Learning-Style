import React from 'react';
import { Filter } from 'lucide-react';

interface HistoryFiltersProps {
  onFilterChange: (filters: any) => void;
}

export const HistoryFilters: React.FC<HistoryFiltersProps> = ({ onFilterChange }) => {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-medium">Filters:</span>
      </div>
      
      <select 
        className="text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500 text-slate-700 dark:text-slate-300"
        onChange={(e) => onFilterChange({ learningStyle: e.target.value })}
      >
        <option value="">Any Style</option>
        <option value="visual">Visual</option>
        <option value="conversational">Conversational</option>
        <option value="step_by_step">Step-by-Step</option>
        <option value="exam_focused">Exam-Focused</option>
        <option value="research_oriented">Research-Oriented</option>
      </select>

      <select 
        className="text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-500 text-slate-700 dark:text-slate-300"
        onChange={(e) => onFilterChange({ difficulty: e.target.value })}
      >
        <option value="">Any Difficulty</option>
        <option value="Beginner">Beginner</option>
        <option value="Intermediate">Intermediate</option>
        <option value="Advanced">Advanced</option>
      </select>
    </div>
  );
};
