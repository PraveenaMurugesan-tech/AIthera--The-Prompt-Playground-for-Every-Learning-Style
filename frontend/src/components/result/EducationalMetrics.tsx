import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Brain, Clock, Activity, GraduationCap } from 'lucide-react';

interface EducationalMetricsProps {
  metrics: {
    difficulty: string;
    bloomLevel: string;
    learningStyle: string;
    estimatedStudyTime: string;
    complexity: string;
  };
}

export const EducationalMetrics: React.FC<EducationalMetricsProps> = ({ metrics }) => {
  const cards = [
    { label: 'Difficulty', value: metrics.difficulty, icon: Activity, color: 'text-orange-500', bg: 'bg-orange-50 dark:bg-orange-500/10' },
    { label: 'Bloom Level', value: metrics.bloomLevel, icon: GraduationCap, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-500/10' },
    { label: 'Learning Style', value: metrics.learningStyle, icon: Brain, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-500/10' },
    { label: 'Study Time', value: metrics.estimatedStudyTime, icon: Clock, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-500/10' },
    { label: 'Complexity', value: metrics.complexity, icon: BookOpen, color: 'text-indigo-500', bg: 'bg-indigo-50 dark:bg-indigo-500/10' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * index }}
            className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col gap-3"
          >
            <div className={`p-2 w-fit rounded-lg ${card.bg} ${card.color}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                {card.label}
              </p>
              <p className="font-semibold text-slate-900 dark:text-white mt-0.5">
                {card.value}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
