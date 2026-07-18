import React from 'react';
import { motion } from 'framer-motion';
import { Bot, CheckCircle2, CircleDashed, Loader2, XCircle } from 'lucide-react';

export interface ExtendedProviderState {
  id: string;
  name: string;
  status: 'Waiting' | 'Processing' | 'Completed' | 'Failed';
  confidence: number;
  responseTime: number;
}

interface ProviderStatusCardProps {
  provider: ExtendedProviderState;
}

export const ProviderStatusCard: React.FC<ProviderStatusCardProps> = ({ provider }) => {
  const statusConfig = {
    Waiting: { icon: CircleDashed, color: 'text-slate-400', border: 'border-slate-200 dark:border-slate-800' },
    Processing: { icon: Loader2, color: 'text-blue-500', border: 'border-blue-500/50' },
    Completed: { icon: CheckCircle2, color: 'text-emerald-500', border: 'border-emerald-500/50' },
    Failed: { icon: XCircle, color: 'text-rose-500', border: 'border-rose-500/50' },
  };

  const config = statusConfig[provider.status];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`bg-white dark:bg-slate-900 rounded-xl p-4 border transition-colors ${config.border}`}
    >
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
            <Bot className="w-5 h-5 text-slate-700 dark:text-slate-300" />
          </div>
          <span className="font-semibold text-slate-900 dark:text-white">
            {provider.name}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${config.color}`}>
            {provider.status}
          </span>
          <Icon className={`w-5 h-5 ${config.color} ${provider.status === 'Processing' ? 'animate-spin' : ''}`} />
        </div>
      </div>

      <div className="space-y-2 mt-4">
        <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>Confidence</span>
          <span>{provider.confidence}%</span>
        </div>
        <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-blue-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${provider.confidence}%` }}
            transition={{ duration: 1 }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-2">
          <span>Response Time</span>
          <span>{provider.responseTime}ms</span>
        </div>
      </div>
    </motion.div>
  );
};
