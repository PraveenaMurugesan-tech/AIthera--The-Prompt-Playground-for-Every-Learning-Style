import React, { useEffect, useState } from 'react';

interface ConsensusMeterProps {
  score: number;
  label: string;
  color: string; // Tailwind color class, e.g., 'text-blue-500'
  strokeColor: string;
}

export const ConsensusMeter: React.FC<ConsensusMeterProps> = ({ score, label, color, strokeColor }) => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    if (current < score) {
      timer = setTimeout(() => setCurrent(prev => prev + 1), 15);
    }
    return () => clearTimeout(timer);
  }, [current, score]);

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (current / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative inline-flex items-center justify-center">
        <svg className="w-40 h-40 transform -rotate-90">
          <circle
            className="text-slate-100 dark:text-slate-800"
            strokeWidth="12"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="80"
            cy="80"
          />
          <circle
            className={strokeColor}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r={radius}
            cx="80"
            cy="80"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className={`text-3xl font-bold ${color}`}>{current}%</span>
        </div>
      </div>
      <span className="mt-4 font-semibold text-slate-700 dark:text-slate-300">{label}</span>
    </div>
  );
};
