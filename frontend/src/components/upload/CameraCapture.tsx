import { useState, useRef, useCallback } from 'react';
import { Camera, X, RefreshCw, Check, AlertCircle } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onCancel: () => void;
}

export const CameraCapture = ({ onCapture, onCancel }: CameraCaptureProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);

  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setError(null);
    } catch (err: unknown) {
      console.error(err);
      setError('Camera access denied or unavailable. Please use file upload instead.');
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  }, [stream]);

  const handleCapture = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        setCapturedImage(canvas.toDataURL('image/jpeg', 0.9));
      }
    }
  }, []);

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleConfirm = useCallback(() => {
    if (capturedImage) {
      // Convert data URL to Blob/File
      fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
          stopCamera();
          onCapture(file);
        });
    }
  }, [capturedImage, onCapture, stopCamera]);

  const handleClose = () => {
    stopCamera();
    onCancel();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 w-full max-w-2xl rounded-2xl overflow-hidden border border-slate-700 shadow-2xl">
        <div className="flex justify-between items-center p-4 border-b border-slate-800">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Camera className="w-5 h-5" />
            Camera Capture
          </h3>
          <button 
            onClick={handleClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="relative aspect-video bg-black flex flex-col items-center justify-center">
          {error ? (
            <div className="text-center p-6 text-slate-300 flex flex-col items-center gap-3">
              <AlertCircle className="w-10 h-10 text-red-500" />
              <p>{error}</p>
            </div>
          ) : (
            <>
              {capturedImage ? (
                <img src={capturedImage} alt="Captured preview" className="w-full h-full object-contain" />
              ) : (
                <video 
                  ref={videoRef} 
                  autoPlay 
                  playsInline 
                  className="w-full h-full object-cover"
                  onCanPlay={() => videoRef.current?.play()}
                />
              )}
              <canvas ref={canvasRef} className="hidden" />
            </>
          )}
          
          {!stream && !error && !capturedImage && (
            <button 
              onClick={startCamera}
              className="absolute px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
            >
              Enable Camera
            </button>
          )}
        </div>
        
        {stream && !error && (
          <div className="p-6 bg-slate-900 border-t border-slate-800 flex justify-center gap-4">
            {!capturedImage ? (
              <button 
                onClick={handleCapture}
                className="w-16 h-16 rounded-full border-4 border-slate-300 flex items-center justify-center bg-white/10 hover:bg-white/20 hover:border-white transition-all"
                title="Capture Photo"
              >
                <div className="w-12 h-12 bg-white rounded-full"></div>
              </button>
            ) : (
              <>
                <button 
                  onClick={handleRetake}
                  className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors border border-slate-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  Retake
                </button>
                <button 
                  onClick={handleConfirm}
                  className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
                >
                  <Check className="w-4 h-4" />
                  Use Photo
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
