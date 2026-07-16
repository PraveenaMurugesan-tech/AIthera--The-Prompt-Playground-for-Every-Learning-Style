import { motion } from 'framer-motion';
import { CheckCircle2, Lock } from 'lucide-react';
import type { LearningPathStep } from '../../types/recommendation';

interface LearningPathProps {
  steps: LearningPathStep[];
}

export const LearningPath = ({ steps }: LearningPathProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <h3 className="font-bold text-lg text-slate-900 dark:text-white mb-6">Learning Path</h3>
      
      <div className="relative">
        {/* Continuous line connecting steps */}
        <div className="absolute top-0 bottom-0 left-3 w-px bg-slate-200 dark:bg-slate-700 -z-10" />
        
        <div className="space-y-6">
          {steps.map((step, index) => {
            const isCompleted = step.status === 'completed';
            const isCurrent = step.status === 'current';
            const isLocked = step.status === 'locked';
            
            return (
              <motion.div 
                key={step.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative flex gap-4 ${isLocked ? 'opacity-50' : ''}`}
              >
                <div className="relative z-10 shrink-0 mt-1">
                  {isCompleted && (
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  )}
                  {isCurrent && (
                    <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 ring-4 ring-blue-50 dark:ring-blue-900/20">
                      <div className="w-2.5 h-2.5 rounded-full bg-blue-600 dark:bg-blue-500 animate-pulse" />
                    </div>
                  )}
                  {isLocked && (
                    <div className="w-6 h-6 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-600 flex items-center justify-center text-slate-400">
                      <Lock className="w-3 h-3" />
                    </div>
                  )}
                </div>
                
                <div>
                  <h4 className={`text-sm font-semibold mb-1 ${
                    isCurrent ? 'text-blue-600 dark:text-blue-400' : 'text-slate-900 dark:text-slate-100'
                  }`}>
                    {step.title}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
