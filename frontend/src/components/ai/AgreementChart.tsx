import React from 'react';
import { motion } from 'framer-motion';

export const AgreementChart: React.FC = () => {
  const data = [
    { label: 'High Agreement', value: 85, color: 'bg-emerald-500' },
    { label: 'Partial Agreement', value: 12, color: 'bg-yellow-500' },
    { label: 'Disagreement', value: 3, color: 'bg-rose-500' },
  ];

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
        Consensus Distribution
      </h4>
      <div className="space-y-3">
        {data.map((item, index) => (
          <div key={item.label} className="space-y-1">
            <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>{item.label}</span>
              <span>{item.value}%</span>
            </div>
            <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
              <motion.div
                className={`h-full ${item.color} rounded-full`}
                initial={{ width: 0 }}
                animate={{ width: `${item.value}%` }}
                transition={{ duration: 1, delay: 0.2 * index }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
