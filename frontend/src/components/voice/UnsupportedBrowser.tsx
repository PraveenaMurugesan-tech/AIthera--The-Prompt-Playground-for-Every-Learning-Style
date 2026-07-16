import { AlertTriangle } from 'lucide-react';

export const UnsupportedBrowser = () => {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-center shadow-sm">
      <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
      <h2 className="text-xl font-semibold mb-2">Browser Not Supported</h2>
      <p className="text-slate-500 dark:text-slate-400 mb-4 max-w-md">
        Voice Learning is not supported in your browser.
        Please use Google Chrome or Microsoft Edge for this feature.
      </p>
    </div>
  );
};
