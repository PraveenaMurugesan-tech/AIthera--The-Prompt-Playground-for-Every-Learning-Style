import React from 'react';
import { motion } from 'framer-motion';

export const TypingAnimation: React.FC = () => {
  return (
    <div className="flex items-center gap-1.5 h-6 px-2">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full"
          animate={{
            y: ['0%', '-50%', '0%'],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.15,
          }}
        />
      ))}
    </div>
  );
};
