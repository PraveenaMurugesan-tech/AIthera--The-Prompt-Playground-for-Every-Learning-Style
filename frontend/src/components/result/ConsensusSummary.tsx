import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, Users } from 'lucide-react';

interface ConsensusSummaryProps {
  summary: string;
}

export const ConsensusSummary: React.FC<ConsensusSummaryProps> = ({ summary }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 p-6"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-yellow-50 dark:bg-yellow-500/10 text-yellow-600 dark:text-yellow-500 rounded-lg">
          <Lightbulb className="w-5 h-5" />
        </div>
        <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          Council Consensus
          <Users className="w-4 h-4 text-slate-400" />
        </h3>
      </div>
      <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-sm md:text-base">
        {summary}
      </p>
    </motion.div>
  );
};
