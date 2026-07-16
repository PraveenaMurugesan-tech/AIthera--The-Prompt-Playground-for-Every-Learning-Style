import { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { Camera, AlertCircle } from 'lucide-react';
import { EmptyUpload } from './EmptyUpload';
import type { ValidationError } from '../../types/upload';

interface UploadDropzoneProps {
  onFileSelect: (file: File) => void;
  onCameraClick: () => void;
  error?: ValidationError | null;
}

export const UploadDropzone = ({ onFileSelect, onCameraClick, error }: UploadDropzoneProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-xl flex items-center gap-3 border border-red-200 dark:border-red-800">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p className="text-sm font-medium">{error.message}</p>
        </div>
      )}

      <div 
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative w-full border-2 border-dashed rounded-2xl transition-all ${
          isDragging 
            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/10 scale-[1.01]' 
            : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800'
        }`}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileInput}
          className="hidden" 
          accept="image/jpeg, image/png, image/webp" 
        />
        
        <EmptyUpload />
      </div>

      <div className="flex items-center gap-4">
        <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
        <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">Capture directly</span>
        <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
      </div>

      <button
        onClick={onCameraClick}
        className="flex items-center justify-center gap-2 w-full py-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 text-slate-700 dark:text-slate-300 font-medium rounded-xl transition-colors shadow-sm"
      >
        <Camera className="w-5 h-5" />
        Use Device Camera
      </button>
    </div>
  );
};
