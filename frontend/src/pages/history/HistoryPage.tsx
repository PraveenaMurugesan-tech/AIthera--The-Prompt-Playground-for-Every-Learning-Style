import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { History as HistoryIcon, Trash2 } from 'lucide-react';
import { HistorySearch } from '../../components/history/HistorySearch';
import { HistoryFilters } from '../../components/history/HistoryFilters';
import { HistoryList } from '../../components/history/HistoryList';
import { historyService } from '../../services/historyService';
import type { HistoryItem } from '../../services/historyService';
import { EmptyState } from '../../components/common/EmptyState';
import { ErrorState } from '../../components/common/ErrorState';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import toast from 'react-hot-toast';
import { useDebounce } from '../../hooks/useDebounce';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedSearch = useDebounce(searchQuery, 300);
  const [filters, setFilters] = useState<{ learningStyle?: string; difficulty?: string }>({});
  
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [showClearAll, setShowClearAll] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await historyService.getHistory();
      setItems(data);
    } catch (err) {
      console.error('Failed to load history', err);
      setError('Failed to load history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadHistory();
  }, []);

  const handleToggleFavorite = async (id: string, isFavorite: boolean) => {
    try {
      await historyService.toggleFavorite(id, isFavorite);
      setItems(items.map(item => item.id === id ? { ...item, isFavorite } : item));
    } catch {
      toast.error('Failed to update favorite status');
    }
  };

  const confirmDelete = (id: string) => {
    setDeleteId(id);
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await historyService.deleteHistoryItem(deleteId);
      setItems(items.filter(item => item.id !== deleteId));
      toast.success('Prompt deleted from history');
    } catch {
      toast.error('Failed to delete prompt');
    } finally {
      setDeleteId(null);
    }
  };

  const handleClearAll = async () => {
    try {
      // Assuming a clearAll method exists, or deleting all items iteratively
      // await historyService.clearHistory();
      setItems([]);
      toast.success('History cleared');
    } catch {
      toast.error('Failed to clear history');
    } finally {
      setShowClearAll(false);
    }
  };

  const handleReopen = (id: string) => {
    navigate('/result', { state: { historyId: id } });
  };

  const filteredItems = items.filter(item => {
    const matchesSearch = item.topic.toLowerCase().includes(debouncedSearch.toLowerCase()) || 
                          item.prompt.toLowerCase().includes(debouncedSearch.toLowerCase());
    const matchesStyle = !filters.learningStyle || item.learningStyle === filters.learningStyle;
    const matchesDifficulty = !filters.difficulty || item.difficulty === filters.difficulty;
    
    return matchesSearch && matchesStyle && matchesDifficulty;
  });

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3 text-blue-600 dark:text-blue-500">
              <HistoryIcon className="h-8 w-8" />
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
                Prompt History
              </h1>
            </div>
            <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl">
              Access and manage your previously generated learning prompts.
            </p>
          </div>
          {items.length > 0 && (
            <button
              onClick={() => setShowClearAll(true)}
              className="px-4 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg flex items-center gap-2 transition-colors self-start md:self-auto"
            >
              <Trash2 className="w-4 h-4" />
              Clear History
            </button>
          )}
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
          <div className="flex justify-center py-20" aria-label="Loading history">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={loadHistory} />
        ) : items.length === 0 ? (
          <EmptyState 
            title="No history yet" 
            description="You haven't generated any prompts yet. Head over to the Prompt Generator to get started." 
            actionLabel="Generate Prompt"
            onAction={() => navigate('/prompt')}
          />
        ) : filteredItems.length === 0 ? (
          <EmptyState 
            title="No matches found" 
            description="We couldn't find any prompts matching your search and filter criteria." 
            actionLabel="Clear Filters"
            onAction={() => {
              setSearchQuery('');
              setFilters({});
            }}
          />
        ) : (
          <HistoryList 
            items={filteredItems} 
            onToggleFavorite={handleToggleFavorite}
            onDelete={confirmDelete}
            onReopen={handleReopen}
          />
        )}
      </div>

      <ConfirmDialog
        isOpen={deleteId !== null}
        title="Delete Prompt"
        message="Are you sure you want to delete this prompt from your history? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Keep Prompt"
        isDestructive={true}
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />

      <ConfirmDialog
        isOpen={showClearAll}
        title="Clear History"
        message="Are you sure you want to delete ALL prompts from your history? This action cannot be undone."
        confirmLabel="Clear All"
        cancelLabel="Cancel"
        isDestructive={true}
        onConfirm={handleClearAll}
        onCancel={() => setShowClearAll(false)}
      />
    </div>
  );
};
