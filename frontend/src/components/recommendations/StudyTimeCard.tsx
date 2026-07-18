import { Target, TrendingUp } from 'lucide-react';
import type { StudyEstimate } from '../../types/recommendation';
import { motion } from 'framer-motion';

interface StudyTimeCardProps {
  estimate: StudyEstimate;
}

export const StudyTimeCard = ({ estimate }: StudyTimeCardProps) => {
  const formatTime = (minutes: number) => {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h > 0 && m > 0) return `${h}h ${m}m`;
    if (h > 0) return `${h}h`;
    return `${m}m`;
  };

  const progressPercentage = Math.min(100, (estimate.completedMinutes / estimate.dailyGoalMinutes) * 100);

  return (
    <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl p-6 text-white shadow-lg relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-black/10 rounded-full blur-xl -ml-8 -mb-8 pointer-events-none" />
      
      <div className="relative z-10">
        <h3 className="font-medium text-indigo-100 mb-1 flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          Estimated Total Study Time
        </h3>
        <p className="text-3xl font-bold mb-8">
          {formatTime(estimate.totalMinutes)}
        </p>
        
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
          <div className="flex justify-between items-end mb-2">
            <div>
              <p className="text-xs font-medium text-indigo-100 mb-1 flex items-center gap-1.5">
                <Target className="w-3.5 h-3.5" />
                Daily Goal
              </p>
              <p className="font-semibold">
                {formatTime(estimate.completedMinutes)} / {formatTime(estimate.dailyGoalMinutes)}
              </p>
            </div>
            <span className="text-sm font-bold">{Math.round(progressPercentage)}%</span>
          </div>
          
          <div className="h-2 w-full bg-black/20 rounded-full overflow-hidden mt-3">
            <motion.div 
              className="h-full bg-white rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
