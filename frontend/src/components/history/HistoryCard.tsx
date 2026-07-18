import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Star, Trash2 } from 'lucide-react';
import type { HistoryItem } from '../../services/historyService';

interface HistoryCardProps {
  item: HistoryItem;
  onToggleFavorite: (id: string, isFavorite: boolean) => void;
  onDelete: (id: string) => void;
  onReopen: (id: string) => void;
}

export const HistoryCard: React.FC<HistoryCardProps> = React.memo(({ item, onToggleFavorite, onDelete, onReopen }) => {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 hover:shadow-md transition-shadow group"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <h4 className="font-semibold text-slate-900 dark:text-white line-clamp-1">{item.topic}</h4>
          <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 dark:text-slate-400">
            <span className="bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">{item.learningStyle}</span>
            <span className="bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">{item.difficulty}</span>
          </div>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onToggleFavorite(item.id, !item.isFavorite)}
            className="p-1.5 text-slate-400 hover:text-yellow-500 transition-colors"
          >
            <Star className={`w-4 h-4 ${item.isFavorite ? 'fill-yellow-500 text-yellow-500' : ''}`} />
          </button>
          <button
            onClick={() => onDelete(item.id)}
            className="p-1.5 text-slate-400 hover:text-rose-500 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-4 leading-relaxed">
        {item.prompt}
      </p>

      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${item.prompt === 'No prompt generated.' || item.prompt === '' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'}`}>
            {item.prompt === 'No prompt generated.' || item.prompt === '' ? 'Failed' : 'Success'}
          </span>
          <span className="text-xs text-slate-400">
            {new Date(item.createdAt).toLocaleString(undefined, {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              hour12: true
            })}
          </span>
        </div>
        <button
          onClick={() => onReopen(item.id)}
          className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-500 dark:hover:text-blue-400"
        >
          <BookOpen className="w-4 h-4" />
          Reopen
        </button>
      </div>
    </motion.div>
  );
});
