import React from 'react';
import { motion } from 'framer-motion';

interface CouncilProgressProps {
  progress: number;
  estimatedTime: number; // in seconds
}

export const CouncilProgress: React.FC<CouncilProgressProps> = ({ progress, estimatedTime }) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-end">
        <div>
          <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Overall Progress
          </h3>
          <div className="text-3xl font-bold text-slate-900 dark:text-white mt-1">
            {Math.round(progress)}%
          </div>
        </div>
        <div className="text-sm font-medium text-slate-500 dark:text-slate-400">
          Estimated time: ~{estimatedTime}s
        </div>
      </div>

      <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-blue-600 dark:bg-blue-500 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
        />
      </div>
    </div>
  );
};
