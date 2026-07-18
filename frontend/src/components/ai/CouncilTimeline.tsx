import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

interface TimelineStep {
  id: string;
  label: string;
  completed: boolean;
  active: boolean;
}

interface CouncilTimelineProps {
  steps: TimelineStep[];
}

export const CouncilTimeline: React.FC<CouncilTimelineProps> = ({ steps }) => {
  return (
    <div className="relative flex items-center justify-between w-full">
      {/* Background line */}
      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-200 dark:bg-slate-800 rounded-full" />
      
      {/* Active progress line */}
      <motion.div
        className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-blue-500 rounded-full z-0"
        initial={{ width: '0%' }}
        animate={{ 
          width: `${(steps.filter(s => s.completed || s.active).length - 1) / (steps.length - 1) * 100}%` 
        }}
        transition={{ duration: 0.5 }}
      />

      {steps.map((step) => (
        <div key={step.id} className="relative z-10 flex flex-col items-center gap-2">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ 
              scale: step.active ? 1.2 : 1,
              backgroundColor: step.completed ? '#3b82f6' : step.active ? '#fff' : '#f8fafc',
              borderColor: step.active || step.completed ? '#3b82f6' : '#cbd5e1'
            }}
            className={`w-8 h-8 rounded-full border-2 flex items-center justify-center transition-colors shadow-sm dark:bg-slate-900`}
          >
            {step.completed && <Check className="w-4 h-4 text-white" />}
            {step.active && !step.completed && <div className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />}
          </motion.div>
          
          <span className={`text-xs md:text-sm font-medium whitespace-nowrap ${
            step.active ? 'text-blue-600 dark:text-blue-400' : 
            step.completed ? 'text-slate-700 dark:text-slate-300' : 
            'text-slate-400'
          }`}>
            {step.label}
          </span>
        </div>
      ))}
    </div>
  );
};
