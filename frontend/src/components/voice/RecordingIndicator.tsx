import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';
import { useEffect, useState } from 'react';

interface RecordingIndicatorProps {
  isRecording: boolean;
}

export const RecordingIndicator = ({ isRecording }: RecordingIndicatorProps) => {
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording) {
      interval = setInterval(() => setDuration(prev => prev + 1), 1000);
    } else {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setDuration(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (!isRecording) return null;

  return (
    <div className="flex items-center gap-4 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-full px-4 py-2">
      <motion.div
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ repeat: Infinity, duration: 1.5 }}
        className="w-2 h-2 rounded-full bg-red-600 dark:bg-red-400"
      />
      <span className="font-medium flex items-center gap-2">
        <Mic className="w-4 h-4" />
        Listening...
      </span>
      <span className="font-mono">{formatDuration(duration)}</span>
      
      <div className="flex items-end gap-1 h-4 ml-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <motion.div
            key={i}
            className="w-1 bg-red-600 dark:bg-red-400 rounded-t-sm"
            animate={{ height: ['20%', '100%', '20%'] }}
            transition={{
              repeat: Infinity,
              duration: 1,
              delay: i * 0.1,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>
    </div>
  );
};
