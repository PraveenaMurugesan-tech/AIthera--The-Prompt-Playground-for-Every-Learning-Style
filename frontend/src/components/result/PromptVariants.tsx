import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, ChevronRight, Wand2 } from 'lucide-react';

interface Variant {
  id: string;
  name: string;
  content: string;
}

interface PromptVariantsProps {
  variants: Variant[];
  selectedVariantId?: string;
  onSelectVariant?: (id: string) => void;
}

export const PromptVariants: React.FC<PromptVariantsProps> = ({ 
  variants, 
  selectedVariantId, 
  onSelectVariant 
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Wand2 className="w-5 h-5 text-indigo-500" />
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">
          Alternative Variants
        </h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {variants.map((variant, index) => {
          const isSelected = variant.id === selectedVariantId;
          
          return (
            <motion.div
              key={variant.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              onClick={() => onSelectVariant?.(variant.id)}
              className={`
                relative p-5 rounded-2xl border transition-all cursor-pointer group
                ${isSelected 
                  ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-500/10 shadow-md' 
                  : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-md'
                }
              `}
            >
              <div className="flex justify-between items-start mb-3">
                <h4 className={`font-semibold ${isSelected ? 'text-indigo-700 dark:text-indigo-400' : 'text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400'}`}>
                  {variant.name}
                </h4>
                {isSelected ? (
                  <CheckCircle2 className="w-5 h-5 text-indigo-500" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </div>
              
              <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3 leading-relaxed">
                {variant.content}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
