import { useState, useCallback, useEffect } from 'react';
import { uploadService } from '../services/uploadService';
import type { UploadFile, UploadState, ValidationError } from '../types/upload';

export function useImageUpload() {
  const [selectedFile, setSelectedFile] = useState<UploadFile | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<ValidationError | null>(null);

  // Cleanup object URLs when component unmounts or file changes
  useEffect(() => {
    return () => {
      if (selectedFile?.previewUrl) {
        uploadService.revokePreviewUrl(selectedFile.previewUrl);
      }
    };
  }, [selectedFile]);

  const handleFileSelect = useCallback((file: File) => {
    setError(null);
    setUploadState('idle');
    setProgress(0);

    const validationError = uploadService.validateImage(file);
    if (validationError) {
      setError(validationError);
      return false;
    }

    // Revoke old URL if it exists
    if (selectedFile?.previewUrl) {
      uploadService.revokePreviewUrl(selectedFile.previewUrl);
    }

    const previewUrl = URL.createObjectURL(file);
    setSelectedFile({
      file,
      previewUrl,
      name: file.name,
      size: file.size,
      type: file.type
    });

    return true;
  }, [selectedFile]);

  const startUpload = useCallback(async () => {
    if (!selectedFile) return;

    setUploadState('uploading');
    setError(null);
    setProgress(0);

    try {
      await uploadService.simulateUpload(selectedFile, (p) => {
        setProgress(p);
      });
      setUploadState('success');
    } catch (err: any) {
      console.error(err);
      setError({
        message: err.message || 'An unknown error occurred during upload',
        code: 'unknown'
      });
      setUploadState('error');
    }
  }, [selectedFile]);

  const removeFile = useCallback(() => {
    if (selectedFile?.previewUrl) {
      uploadService.revokePreviewUrl(selectedFile.previewUrl);
    }
    setSelectedFile(null);
    setUploadState('idle');
    setProgress(0);
    setError(null);
  }, [selectedFile]);

  return {
    selectedFile,
    uploadState,
    progress,
    error,
    handleFileSelect,
    startUpload,
    removeFile
  };
}
