import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History as HistoryIcon } from 'lucide-react';
import { HistorySearch } from '../../components/history/HistorySearch';
import { HistoryFilters } from '../../components/history/HistoryFilters';
import { HistoryList } from '../../components/history/HistoryList';
import { EmptyHistory } from '../../components/history/EmptyHistory';
import { historyService } from '../../services/historyService';
import type { HistoryItem } from '../../services/historyService';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<{ learningStyle?: string; difficulty?: string }>({});

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await historyService.getHistory();
      setItems(data);
    } catch (error) {
      console.error('Failed to load history', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleToggleFavorite = async (id: string, isFavorite: boolean) => {
    await historyService.toggleFavorite(id, isFavorite);
    setItems(items.map(item => item.id === id ? { ...item, isFavorite } : item));
  };

  const handleDelete = async (id: string) => {
    await historyService.deleteHistoryItem(id);
    setItems(items.filter(item => item.id !== id));
  };

  const handleReopen = (id: string) => {
    // In a real app, this would fetch the full result and navigate to /result with that data
    navigate('/result', { state: { historyId: id } });
  };

  const filteredItems = items.filter(item => {
    const matchesSearch = item.topic.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          item.prompt.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStyle = !filters.learningStyle || item.learningStyle === filters.learningStyle;
    const matchesDifficulty = !filters.difficulty || item.difficulty === filters.difficulty;
    
    return matchesSearch && matchesStyle && matchesDifficulty;
  });

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col gap-2">
          <div className="flex items-center gap-3 text-blue-600 dark:text-blue-500">
            <HistoryIcon className="h-8 w-8" />
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
              Prompt History
            </h1>
          </div>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl">
            Access and manage your previously generated learning prompts.
          </p>
        </header>

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
          <div className="w-full md:w-96">
            <HistorySearch value={searchQuery} onChange={setSearchQuery} />
          </div>
          <HistoryFilters onFilterChange={(newFilters) => setFilters(prev => ({ ...prev, ...newFilters }))} />
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : items.length === 0 ? (
          <EmptyHistory />
        ) : filteredItems.length === 0 ? (
          <div className="text-center py-20 text-slate-500 dark:text-slate-400">
            No prompts found matching your filters.
          </div>
        ) : (
          <HistoryList 
            items={filteredItems} 
            onToggleFavorite={handleToggleFavorite}
            onDelete={handleDelete}
            onReopen={handleReopen}
          />
        )}
      </div>
    </div>
  );
};
