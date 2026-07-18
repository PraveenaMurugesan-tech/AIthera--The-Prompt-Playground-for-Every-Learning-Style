import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit } from 'lucide-react';

interface ConsensusAnimationProps {
  progress: number;
}

export const ConsensusAnimation: React.FC<ConsensusAnimationProps> = ({ progress }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-6">
      <div className="relative flex items-center justify-center w-32 h-32">
        {/* Background pulsing rings */}
        <motion.div
          className="absolute inset-0 rounded-full border-4 border-blue-500/20 dark:border-blue-400/20"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute inset-2 rounded-full border-4 border-indigo-500/30 dark:border-indigo-400/30"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.8, 0, 0.8],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 0.3,
          }}
        />
        
        {/* Central Icon */}
        <div className="absolute z-10 flex items-center justify-center w-16 h-16 bg-white dark:bg-slate-900 rounded-full shadow-lg border border-slate-100 dark:border-slate-800">
          <BrainCircuit className="w-8 h-8 text-blue-600 dark:text-blue-400" />
        </div>
        
        {/* Orbiting dots representing AI models */}
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className="absolute w-3 h-3 bg-blue-500 dark:bg-blue-400 rounded-full"
            style={{
              top: '50%',
              left: '50%',
              marginTop: '-6px',
              marginLeft: '-6px',
            }}
            animate={{
              rotate: 360,
              x: 45,
            }}
            transition={{
              rotate: {
                duration: 3 + index,
                repeat: Infinity,
                ease: "linear",
              },
              x: {
                duration: 0,
              }
            }}
            initial={{ rotate: index * 120 }}
          />
        ))}
      </div>

      <div className="text-center">
        <h3 className="text-xl font-semibold text-slate-900 dark:text-white">
          Building AI Consensus...
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
          {progress < 100 
            ? "Combining insights from top models for the perfect prompt."
            : "Consensus reached! Finalizing results..."}
        </p>
      </div>
    </div>
  );
};
