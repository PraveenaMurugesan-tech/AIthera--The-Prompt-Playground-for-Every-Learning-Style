import { FileImage, CheckCircle, XCircle } from 'lucide-react';
import type { UploadFile, UploadState } from '../../types/upload';

interface FileDetailsProps {
  file: UploadFile;
  uploadState: UploadState;
}

export const FileDetails = ({ file, uploadState }: FileDetailsProps) => {
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-700">
      <div className="p-3 bg-white dark:bg-slate-800 rounded-lg shadow-sm">
        <FileImage className="w-6 h-6 text-blue-600 dark:text-blue-400" />
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
          {file.name}
        </p>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-xs text-slate-500 dark:text-slate-400">
            {formatBytes(file.size)}
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400 uppercase">
            {file.type.split('/')[1] || 'IMAGE'}
          </span>
        </div>
      </div>
      
      <div className="flex items-center justify-center w-8 h-8">
        {uploadState === 'success' && (
          <CheckCircle className="w-6 h-6 text-green-500" />
        )}
        {uploadState === 'error' && (
          <XCircle className="w-6 h-6 text-red-500" />
        )}
      </div>
    </div>
  );
};
