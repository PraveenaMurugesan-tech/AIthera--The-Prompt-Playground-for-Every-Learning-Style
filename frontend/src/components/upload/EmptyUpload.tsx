import { UploadCloud, Image as ImageIcon } from 'lucide-react';

export const EmptyUpload = () => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center pointer-events-none">
      <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center mb-4">
        <UploadCloud className="w-8 h-8" />
      </div>
      
      <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
        Drag and drop an educational image
      </h3>
      
      <div className="flex items-center gap-4 my-2 w-full max-w-xs">
        <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
        <span className="text-sm text-slate-500 dark:text-slate-400 font-medium">or</span>
        <div className="h-px bg-slate-200 dark:bg-slate-700 flex-1"></div>
      </div>
      
      <span className="inline-block mt-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors shadow-sm pointer-events-auto cursor-pointer">
        Browse Files
      </span>
      
      <div className="mt-6 flex flex-col items-center gap-2">
        <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
          <ImageIcon className="w-4 h-4" />
          <span>Supported: PNG • JPG • WEBP</span>
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-500">
          Maximum file size: 10 MB
        </p>
      </div>
    </div>
  );
};
