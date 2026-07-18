import React, { useState } from 'react';
import { Copy, Share2, Bookmark, Download, RefreshCw, CheckCircle2 } from 'lucide-react';

interface PromptToolbarProps {
  promptText: string;
}

export const PromptToolbar: React.FC<PromptToolbarProps> = ({ promptText }) => {
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const [bookmarked, setBookmarked] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(promptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const simulateAction = (action: string) => {
    setLoading(action);
    setTimeout(() => setLoading(null), 1000);
  };

  const handleDownload = (type: 'txt' | 'pdf') => {
    simulateAction(`download-${type}`);
    // Mocking download behavior
    if (type === 'txt') {
      const element = document.createElement("a");
      const file = new Blob([promptText], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = "prompt.txt";
      document.body.appendChild(element);
      element.click();
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-2 mt-4 p-2 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700">
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors"
      >
        {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
        {copied ? 'Copied' : 'Copy'}
      </button>

      <div className="w-px h-4 bg-slate-300 dark:bg-slate-600 mx-1"></div>

      <button
        onClick={() => simulateAction('regenerate')}
        disabled={loading !== null}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
      >
        <RefreshCw className={`w-4 h-4 ${loading === 'regenerate' ? 'animate-spin' : ''}`} />
        Regenerate
      </button>

      <button
        onClick={() => setBookmarked(!bookmarked)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors"
      >
        <Bookmark className={`w-4 h-4 ${bookmarked ? 'fill-blue-500 text-blue-500' : ''}`} />
        Save
      </button>

      <button
        onClick={() => simulateAction('share')}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors"
      >
        <Share2 className="w-4 h-4" />
        Share
      </button>

      <div className="w-px h-4 bg-slate-300 dark:bg-slate-600 mx-1"></div>

      <button
        onClick={() => handleDownload('txt')}
        disabled={loading !== null}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
      >
        <Download className="w-4 h-4" />
        .TXT
      </button>

      <button
        onClick={() => handleDownload('pdf')}
        disabled={loading !== null}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
      >
        <Download className="w-4 h-4" />
        .PDF
      </button>
    </div>
  );
};
