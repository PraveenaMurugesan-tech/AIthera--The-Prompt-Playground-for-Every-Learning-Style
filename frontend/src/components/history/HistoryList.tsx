import React from 'react';
import { HistoryCard } from './HistoryCard';
import type { HistoryItem } from '../../services/historyService';

interface HistoryListProps {
  items: HistoryItem[];
  onToggleFavorite: (id: string, isFavorite: boolean) => void;
  onDelete: (id: string) => void;
  onReopen: (id: string) => void;
}

export const HistoryList: React.FC<HistoryListProps> = ({ items, onToggleFavorite, onDelete, onReopen }) => {
  // Group items by date
  const grouped = items.reduce((acc, item) => {
    const date = new Date(item.createdAt);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    let group = 'Older';
    if (date.toDateString() === today.toDateString()) {
      group = 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      group = 'Yesterday';
    } else if (today.getTime() - date.getTime() < 7 * 24 * 60 * 60 * 1000) {
      group = 'Last Week';
    }

    if (!acc[group]) acc[group] = [];
    acc[group].push(item);
    return acc;
  }, {} as Record<string, HistoryItem[]>);

  const groupOrder = ['Today', 'Yesterday', 'Last Week', 'Older'];

  return (
    <div className="space-y-8">
      {groupOrder.map(group => {
        const groupItems = grouped[group];
        if (!groupItems || groupItems.length === 0) return null;

        return (
          <div key={group} className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
              {group}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {groupItems.map(item => (
                <HistoryCard
                  key={item.id}
                  item={item}
                  onToggleFavorite={onToggleFavorite}
                  onDelete={onDelete}
                  onReopen={onReopen}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};
