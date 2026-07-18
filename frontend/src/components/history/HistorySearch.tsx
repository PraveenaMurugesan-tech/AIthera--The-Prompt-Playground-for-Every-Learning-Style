import React from 'react';
import { Search } from 'lucide-react';

interface HistorySearchProps {
  value: string;
  onChange: (value: string) => void;
}

export const HistorySearch: React.FC<HistorySearchProps> = ({ value, onChange }) => {
  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-slate-400" />
      </div>
      <input
        type="text"
        className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 dark:border-slate-700 rounded-xl leading-5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
        placeholder="Search prompt history..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
};
