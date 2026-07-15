import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, Target } from 'lucide-react';

interface CircularProgressProps {
  percentage: number;
  colorClass: string;
}

const CircularProgress: React.FC<CircularProgressProps> = ({ percentage, colorClass }) => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    let timer: any;
    if (current < percentage) {
      timer = setTimeout(() => setCurrent(prev => prev + 1), 20);
    }
    return () => clearTimeout(timer);
  }, [current, percentage]);

  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (current / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="w-24 h-24 transform -rotate-90">
        <circle
          className="text-slate-100 dark:text-slate-800"
          strokeWidth="8"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx="48"
          cy="48"
        />
        <circle
          className={colorClass}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx="48"
          cy="48"
        />
      </svg>
      <div className="absolute text-xl font-bold text-slate-900 dark:text-white">
        {current}%
      </div>
    </div>
  );
};

interface ScoreCardsProps {
  confidence: number;
  agreement: number;
}

export const ScoreCards: React.FC<ScoreCardsProps> = ({ confidence, agreement }) => {
  return (
    <div className="grid grid-cols-2 gap-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col items-center text-center gap-3"
      >
        <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-500 font-medium">
          <ShieldCheck className="w-5 h-5" />
          <span>Confidence Score</span>
        </div>
        <CircularProgress percentage={confidence} colorClass="text-emerald-500" />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col items-center text-center gap-3"
      >
        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-500 font-medium">
          <Target className="w-5 h-5" />
          <span>Agreement Score</span>
        </div>
        <CircularProgress percentage={agreement} colorClass="text-blue-500" />
      </motion.div>
    </div>
  );
};
