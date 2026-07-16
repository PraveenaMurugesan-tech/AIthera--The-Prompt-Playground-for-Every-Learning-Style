import { UploadCloud, RefreshCw, Trash2, Wand2, Download } from 'lucide-react';
import type { UploadState } from '../../types/upload';

interface UploadToolbarProps {
  uploadState: UploadState;
  onUpload: () => void;
  onReplace: () => void;
  onRemove: () => void;
  onAnalyze: () => void;
  previewUrl?: string;
}

export const UploadToolbar = ({
  uploadState,
  onUpload,
  onReplace,
  onRemove,
  onAnalyze,
  previewUrl
}: UploadToolbarProps) => {
  
  const isUploading = uploadState === 'uploading';
  const isSuccess = uploadState === 'success';

  const handleDownload = () => {
    if (!previewUrl) return;
    const link = document.createElement('a');
    link.href = previewUrl;
    link.download = 'aithera_uploaded_image';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
      <div className="flex flex-wrap items-center gap-3">
        {uploadState === 'idle' || uploadState === 'error' ? (
          <button
            onClick={onUpload}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-sm"
          >
            <UploadCloud className="w-4 h-4" />
            Upload Image
          </button>
        ) : (
          <button
            onClick={onReplace}
            disabled={isUploading}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-medium transition-colors border border-slate-200 dark:border-slate-700 disabled:opacity-50"
          >
            <RefreshCw className="w-4 h-4" />
            Replace
          </button>
        )}
        
        <button
          onClick={onRemove}
          disabled={isUploading}
          className="flex items-center gap-2 px-4 py-2.5 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 font-medium transition-colors disabled:opacity-50"
        >
          <Trash2 className="w-4 h-4" />
          Remove
        </button>
      </div>
      
      <div className="flex flex-wrap items-center gap-3">
        {isSuccess && (
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2.5 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            Download
          </button>
        )}
        
        <div className="relative group">
          <button
            onClick={onAnalyze}
            disabled={!isSuccess}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white hover:bg-indigo-700 rounded-xl font-medium transition-all shadow-sm disabled:opacity-50 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:text-slate-500"
          >
            <Wand2 className="w-4 h-4" />
            Analyze Image
          </button>
        </div>
      </div>
    </div>
  );
};
