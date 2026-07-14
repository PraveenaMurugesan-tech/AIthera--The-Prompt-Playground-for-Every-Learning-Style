import React from 'react';
import { Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

interface GenerateButtonProps {
  onClick: () => void;
  disabled: boolean;
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({ onClick, disabled }) => {
  return (
    <motion.button
      type="button"
      onClick={onClick}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      className={`w-full py-4 px-6 rounded-xl flex items-center justify-center gap-2 text-lg font-semibold transition-all shadow-md
        ${
          disabled
            ? 'bg-slate-200 text-slate-400 cursor-not-allowed dark:bg-slate-700/50 dark:text-slate-500 shadow-none'
            : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg dark:bg-blue-600 dark:hover:bg-blue-500'
        }
      `}
    >
      <Sparkles className="h-5 w-5" />
      Generate Prompt
    </motion.button>
  );
};
