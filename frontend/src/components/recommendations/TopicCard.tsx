import { Star } from 'lucide-react';
import type { Difficulty } from '../../types/recommendation';
import { DifficultyBadge } from './DifficultyBadge';

interface TopicCardProps {
  title: string;
  difficulty: Difficulty;
  isRecommendedNext?: boolean;
  onClick?: () => void;
}

export const TopicCard = ({ title, difficulty, isRecommendedNext, onClick }: TopicCardProps) => {
  const renderStars = () => {
    let activeStars = 1;
    if (difficulty === 'Intermediate') activeStars = 2;
    if (difficulty === 'Advanced') activeStars = 3;

    return (
      <div className="flex gap-0.5">
        {[1, 2, 3].map((star) => (
          <Star 
            key={star} 
            className={`w-3.5 h-3.5 ${
              star <= activeStars 
                ? 'fill-yellow-400 text-yellow-400' 
                : 'text-slate-300 dark:text-slate-600'
            }`} 
          />
        ))}
      </div>
    );
  };

  return (
    <div 
      onClick={onClick}
      className={`p-4 rounded-xl border flex flex-col gap-3 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''} ${
      isRecommendedNext 
        ? 'bg-blue-50/50 dark:bg-blue-900/10 border-blue-200 dark:border-blue-800' 
        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700'
    }`}>
      <div className="flex justify-between items-start gap-2">
        <h4 className="font-semibold text-slate-900 dark:text-slate-100 text-sm leading-tight">
          {title}
        </h4>
        {renderStars()}
      </div>
      
      <div className="flex items-center justify-between mt-auto">
        <DifficultyBadge difficulty={difficulty} />
        {isRecommendedNext && (
          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
            Next Up
          </span>
        )}
      </div>
    </div>
  );
};
