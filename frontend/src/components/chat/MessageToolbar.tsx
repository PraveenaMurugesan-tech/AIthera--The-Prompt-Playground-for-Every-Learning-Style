import React, { useState } from 'react';
import { Copy, RefreshCw, Bookmark, Share2, CheckCircle2 } from 'lucide-react';

interface MessageToolbarProps {
  text: string;
}

export const MessageToolbar: React.FC<MessageToolbarProps> = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button 
        onClick={handleCopy}
        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
        title="Copy"
      >
        {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
      </button>
      <button 
        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
        title="Regenerate"
      >
        <RefreshCw className="w-4 h-4" />
      </button>
      <button 
        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
        title="Bookmark"
      >
        <Bookmark className="w-4 h-4" />
      </button>
      <button 
        className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
        title="Share"
      >
        <Share2 className="w-4 h-4" />
      </button>
    </div>
  );
};
