import { Lightbulb, CheckCircle2, AlertCircle } from 'lucide-react';

export const UploadTips = () => {
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 shadow-sm text-slate-900 dark:text-slate-100">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-yellow-500" />
        <h3 className="font-semibold text-lg">Best Results</h3>
      </div>
      
      <ul className="space-y-3">
        <li className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
          <span className="text-sm text-slate-600 dark:text-slate-300">
            Upload high-resolution images
          </span>
        </li>
        <li className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
          <span className="text-sm text-slate-600 dark:text-slate-300">
            Ensure diagrams and text are clearly visible
          </span>
        </li>
        <li className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-orange-500 shrink-0 mt-0.5" />
          <span className="text-sm text-slate-600 dark:text-slate-300">
            Avoid blurry or extremely dark photos
          </span>
        </li>
        <li className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
          <span className="text-sm text-slate-600 dark:text-slate-300">
            Supported formats: JPG, PNG, WEBP (Max 10MB)
          </span>
        </li>
      </ul>
    </div>
  );
};
