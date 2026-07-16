import { Network, ArrowRight } from 'lucide-react';
import type { RelatedTopic } from '../../types/recommendation';

interface RelatedTopicsProps {
  topics: RelatedTopic[];
}

export const RelatedTopics = ({ topics }: RelatedTopicsProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-5">
        <Network className="w-5 h-5 text-emerald-500" />
        <h3 className="font-bold text-lg text-slate-900 dark:text-white">Related Concepts</h3>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <button 
            key={topic.id}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 hover:bg-emerald-50 dark:bg-slate-900/50 dark:hover:bg-emerald-900/20 text-slate-700 dark:text-slate-300 hover:text-emerald-700 dark:hover:text-emerald-400 border border-slate-200 dark:border-slate-700 hover:border-emerald-200 dark:hover:border-emerald-800/50 rounded-lg text-sm font-medium transition-colors group"
          >
            {topic.title}
            <ArrowRight className="w-3.5 h-3.5 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
          </button>
        ))}
      </div>
    </div>
  );
};
