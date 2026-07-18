export type UploadState = 'idle' | 'uploading' | 'success' | 'error';

export interface UploadFile {
  file: File;
  previewUrl: string;
  name: string;
  size: number;
  type: string;
}

export interface ValidationError {
  message: string;
  code: 'file_too_large' | 'invalid_type' | 'corrupted' | 'unknown';
}

export const SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/webp'];
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
