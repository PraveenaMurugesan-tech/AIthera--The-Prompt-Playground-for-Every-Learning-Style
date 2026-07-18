import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useImageUpload } from '../../hooks/useImageUpload';
import { UploadDropzone } from '../../components/upload/UploadDropzone';
import { ImagePreview } from '../../components/upload/ImagePreview';
import { UploadToolbar } from '../../components/upload/UploadToolbar';
import { UploadProgress } from '../../components/upload/UploadProgress';
import { CameraCapture } from '../../components/upload/CameraCapture';
import { FileDetails } from '../../components/upload/FileDetails';
import { UploadTips } from '../../components/upload/UploadTips';
import { Image } from 'lucide-react';
import { analyzeImage } from '../../services/api';
import toast from 'react-hot-toast';
import { validateFileSize, validateFileType } from '../../utils/validation';

export const UploadPage = () => {
  const {
    selectedFile,
    uploadState,
    progress,
    error,
    handleFileSelect,
    startUpload,
    removeFile
  } = useImageUpload();

  const [showCamera, setShowCamera] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleReplaceClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      
      if (!validateFileType(file)) {
        toast.error('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
        return;
      }
      if (!validateFileSize(file, 5)) {
        toast.error('File is too large. Maximum size is 5MB.');
        return;
      }
      
      handleFileSelect(file);
    }
  };

  const handleFileDrop = (file: File) => {
    if (!validateFileType(file)) {
      toast.error('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
      return;
    }
    if (!validateFileSize(file, 5)) {
      toast.error('File is too large. Maximum size is 5MB.');
      return;
    }
    handleFileSelect(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile?.file) return;

    setIsAnalyzing(true);
    const toastId = toast.loading('Analyzing image...');

    try {
      const result = await analyzeImage(selectedFile.file);
      toast.success('Analysis complete!', { id: toastId });
      
      navigate('/loading', {
        state: {
          formData: {
            topic: result.topic,
            learningStyle: 'visual',
            difficulty: 'intermediate',
            bloomLevel: 'apply',
            instructions: result.instructions || 'Generated from Image Analysis'
          }
        }
      });
    } catch (err) {
      console.error("Analysis failed:", err);
      toast.error('Failed to analyze image.', { id: toastId });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex-1 overflow-auto bg-slate-50 dark:bg-slate-900 p-4 md:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl text-blue-600 dark:text-blue-400">
              <Image className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Image Upload</h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400 text-lg max-w-2xl">
            Upload or capture educational images, diagrams, or handwritten notes for AI analysis and interpretation.
          </p>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Upload Area & Preview */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            {!selectedFile ? (
              <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-6 rounded-2xl shadow-sm">
                <UploadDropzone 
                  onFileSelect={handleFileDrop} 
                  onCameraClick={() => setShowCamera(true)}
                  error={error}
                />
              </div>
            ) : (
              <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-6 rounded-2xl shadow-sm">
                <ImagePreview 
                  previewUrl={selectedFile.previewUrl} 
                  filename={selectedFile.name} 
                />
                
                <div className="mt-6">
                  <FileDetails file={selectedFile} uploadState={uploadState} />
                </div>

                <UploadProgress progress={progress} uploadState={uploadState} />

                <UploadToolbar 
                  uploadState={uploadState}
                  onUpload={startUpload}
                  onReplace={handleReplaceClick}
                  onRemove={removeFile}
                  onAnalyze={handleAnalyze}
                  previewUrl={selectedFile.previewUrl}
                  disabled={isAnalyzing}
                />

                {/* Hidden input for the Replace action */}
                <input 
                  type="file" 
                  ref={fileInputRef}
                  onChange={handleFileInput}
                  className="hidden" 
                  accept="image/jpeg, image/png, image/webp" 
                  aria-label="Upload image"
                />
              </div>
            )}
          </div>

          {/* Right Column: Tips & Guidelines */}
          <div className="flex flex-col gap-6">
            <UploadTips />
          </div>

        </div>
      </div>

      {showCamera && (
        <CameraCapture 
          onCapture={(file) => {
            handleFileDrop(file);
            setShowCamera(false);
          }} 
          onCancel={() => setShowCamera(false)} 
        />
      )}
    </div>
  );
};
