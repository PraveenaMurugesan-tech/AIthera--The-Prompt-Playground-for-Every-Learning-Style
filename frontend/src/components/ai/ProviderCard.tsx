import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, CircleDashed, Loader2, XCircle, Bot } from 'lucide-react';
import type { ProviderState } from '../../services/promptService';

interface ProviderCardProps {
  provider: ProviderState;
}

const statusConfig = {
  Waiting: {
    icon: CircleDashed,
    color: 'text-slate-400 dark:text-slate-500',
    bg: 'bg-slate-50 dark:bg-slate-800/50',
    border: 'border-slate-200 dark:border-slate-700',
    animation: {}
  },
  Processing: {
    icon: Loader2,
    color: 'text-blue-500 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-500/10',
    border: 'border-blue-200 dark:border-blue-500/20',
    animation: { rotate: 360 }
  },
  Completed: {
    icon: CheckCircle2,
    color: 'text-emerald-500 dark:text-emerald-400',
    bg: 'bg-emerald-50 dark:bg-emerald-500/10',
    border: 'border-emerald-200 dark:border-emerald-500/20',
    animation: {}
  },
  Failed: {
    icon: XCircle,
    color: 'text-rose-500 dark:text-rose-400',
    bg: 'bg-rose-50 dark:bg-rose-500/10',
    border: 'border-rose-200 dark:border-rose-500/20',
    animation: {}
  }
};

export const ProviderCard: React.FC<ProviderCardProps> = ({ provider }) => {
  const config = statusConfig[provider.status];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex items-center justify-between p-4 rounded-xl border ${config.bg} ${config.border} transition-colors duration-300`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-white dark:bg-slate-900 shadow-sm`}>
          <Bot className="w-5 h-5 text-slate-700 dark:text-slate-300" />
        </div>
        <span className="font-medium text-slate-900 dark:text-white">
          {provider.name}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <span className={`text-sm font-medium ${config.color}`}>
          {provider.status}
        </span>
        <motion.div
          animate={config.animation}
          transition={
            provider.status === 'Processing'
              ? { duration: 2, repeat: Infinity, ease: "linear" }
              : {}
          }
        >
          <Icon className={`w-5 h-5 ${config.color}`} />
        </motion.div>
      </div>
    </motion.div>
  );
};
