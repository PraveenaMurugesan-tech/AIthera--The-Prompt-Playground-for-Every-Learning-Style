import type { UploadFile, ValidationError } from '../types/upload';
import { SUPPORTED_FORMATS, MAX_FILE_SIZE } from '../types/upload';

class UploadService {
  public validateImage(file: File): ValidationError | null {
    if (!SUPPORTED_FORMATS.includes(file.type)) {
      return {
        message: 'Unsupported file type. Please upload a JPG, PNG, or WEBP image.',
        code: 'invalid_type'
      };
    }

    if (file.size > MAX_FILE_SIZE) {
      return {
        message: 'File is too large. Maximum size is 10 MB.',
        code: 'file_too_large'
      };
    }

    return null;
  }

  public simulateUpload(
    _file: UploadFile,
    onProgress: (progress: number) => void
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      let progress = 0;
      
      const interval = setInterval(() => {
        // Random progress increment between 5% and 20%
        progress += Math.floor(Math.random() * 15) + 5;
        
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          onProgress(progress);
          
          // Randomly fail sometimes to show error handling (5% chance)
          if (Math.random() < 0.05) {
            reject(new Error('Upload failed. Please try again.'));
          } else {
            // Mock backend URL
            resolve(`mock_url_${Date.now()}`);
          }
        } else {
          onProgress(progress);
        }
      }, 300); // Update every 300ms
    });
  }

  public revokePreviewUrl(url: string | null) {
    if (url) {
      URL.revokeObjectURL(url);
    }
  }
}

export const uploadService = new UploadService();
