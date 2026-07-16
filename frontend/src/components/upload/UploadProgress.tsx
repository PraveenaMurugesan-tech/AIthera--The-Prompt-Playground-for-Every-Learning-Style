import { motion } from 'framer-motion';
import type { UploadState } from '../../types/upload';
import { Loader2 } from 'lucide-react';

interface UploadProgressProps {
  progress: number;
  uploadState: UploadState;
}

export const UploadProgress = ({ progress, uploadState }: UploadProgressProps) => {
  if (uploadState === 'idle' || uploadState === 'error') {
    return null;
  }

  const isComplete = progress >= 100 || uploadState === 'success';

  return (
    <div className="mt-4 p-5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {!isComplete && <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />}
          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
            {isComplete ? 'Upload Complete' : 'Uploading...'}
          </span>
        </div>
        <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
          {Math.min(100, progress)}%
        </span>
      </div>
      
      <div className="h-3 w-full bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden border border-slate-200 dark:border-slate-700/50">
        <motion.div 
          className="h-full bg-blue-600 rounded-full relative"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: "easeOut", duration: 0.3 }}
        >
          <div className="absolute top-0 bottom-0 left-0 right-0 overflow-hidden">
            {!isComplete && (
              <motion.div
                className="w-[200%] h-full bg-[linear-gradient(90deg,transparent_25%,rgba(255,255,255,0.3)_50%,transparent_75%)]"
                animate={{ x: ['-100%', '0%'] }}
                transition={{
                  repeat: Infinity,
                  duration: 1.5,
                  ease: "linear"
                }}
              />
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};
