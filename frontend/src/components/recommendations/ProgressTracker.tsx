import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';
import type { SkillProgress } from '../../types/recommendation';

interface ProgressTrackerProps {
  skills: SkillProgress[];
}

export const ProgressTracker = ({ skills }: ProgressTrackerProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-orange-500" />
        <h3 className="font-bold text-lg text-slate-900 dark:text-white">Skill Progress</h3>
      </div>
      
      <div className="space-y-5">
        {skills.map((skill, index) => (
          <div key={skill.skill}>
            <div className="flex justify-between items-end mb-2">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {skill.skill}
              </span>
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">
                {skill.percentage}%
              </span>
            </div>
            
            <div className="h-2.5 w-full bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden border border-slate-200 dark:border-slate-700/50">
              <motion.div 
                className="h-full bg-orange-500 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${skill.percentage}%` }}
                transition={{ duration: 1, delay: index * 0.1, ease: "easeOut" }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
