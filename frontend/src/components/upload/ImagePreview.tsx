import { useState } from 'react';
import { Maximize2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ImagePreviewProps {
  previewUrl: string;
  filename: string;
}

export const ImagePreview = ({ previewUrl, filename }: ImagePreviewProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <div className="relative group w-full aspect-video md:aspect-auto md:h-[400px] bg-slate-100 dark:bg-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 flex items-center justify-center">
        <img 
          src={previewUrl} 
          alt={filename} 
          className="w-full h-full object-contain"
        />
        
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button 
            onClick={() => setIsExpanded(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white rounded-xl font-medium transition-colors border border-white/30"
          >
            <Maximize2 className="w-4 h-4" />
            Expand Preview
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 p-4 md:p-10"
          >
            <button 
              onClick={() => setIsExpanded(false)}
              className="absolute top-6 right-6 p-3 text-white/70 hover:text-white bg-black/50 hover:bg-black/80 rounded-xl transition-colors z-10"
            >
              <X className="w-6 h-6" />
            </button>
            
            <motion.img 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              src={previewUrl} 
              alt={filename} 
              className="w-full h-full object-contain"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
