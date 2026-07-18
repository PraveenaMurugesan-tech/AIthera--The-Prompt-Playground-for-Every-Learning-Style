import { Clock, Bookmark, PlayCircle } from 'lucide-react';
import type { Recommendation } from '../../types/recommendation';
import { DifficultyBadge } from './DifficultyBadge';

interface RecommendationCardProps {
  recommendation: Recommendation;
}

export const RecommendationCard = ({ recommendation }: RecommendationCardProps) => {
  return (
    <div className={`p-5 rounded-xl border transition-all hover:shadow-md ${
      recommendation.isPriority 
        ? 'bg-blue-50/50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800/50' 
        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
    }`}>
      <div className="flex items-start justify-between gap-4 mb-3">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              {recommendation.category}
            </span>
            {recommendation.isPriority && (
              <span className="text-[10px] font-bold uppercase tracking-wider bg-blue-600 text-white px-2 py-0.5 rounded-full">
                Recommended Next
              </span>
            )}
          </div>
          <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100 leading-tight">
            {recommendation.title}
          </h3>
        </div>
        <button className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
          <Bookmark className="w-5 h-5" />
        </button>
      </div>
      
      <p className="text-slate-600 dark:text-slate-300 text-sm mb-4 line-clamp-2">
        {recommendation.description}
      </p>
      
      <div className="flex items-center justify-between mt-auto">
        <div className="flex items-center gap-3">
          <DifficultyBadge difficulty={recommendation.difficulty} />
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>
              {Math.floor(recommendation.estimatedMinutes / 60) > 0 && `${Math.floor(recommendation.estimatedMinutes / 60)}h `}
              {recommendation.estimatedMinutes % 60 > 0 && `${recommendation.estimatedMinutes % 60}m`}
            </span>
          </div>
        </div>
        
        <button className="flex items-center gap-1.5 text-sm font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
          <PlayCircle className="w-4 h-4" />
          Start
        </button>
      </div>
    </div>
  );
};
