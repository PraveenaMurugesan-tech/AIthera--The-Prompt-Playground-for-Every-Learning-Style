import { useRef, useState, useEffect, type DragEvent, type ChangeEvent } from 'react'
import { Button } from '../common/Button'

export type UploadedFile = {
  id: string
  name: string
  url: string
  size: number
  progress: number
  status: 'uploading' | 'success' | 'error'
  errorMsg?: string
}

type ImageUploadProps = {
  onChange?: (files: UploadedFile[]) => void
  maxFiles?: number
  maxSizeMB?: number
}

export const ImageUpload = ({ onChange, maxFiles = 3, maxSizeMB = 5 }: ImageUploadProps) => {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Camera State
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [cameraSupported, setCameraSupported] = useState(true)

  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  // Notify parent component of file list changes
  useEffect(() => {
    if (onChange) {
      onChange(files)
    }
  }, [files, onChange])

  // Stop camera stream when component unmounts
  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [cameraStream])

  // Handlers for Drag and Drop
  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    setErrorMessage(null)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files)
    }
  }

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null)
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files)
    }
  }

  // Core file validation and uploading simulation
  const processFiles = (selectedList: FileList) => {
    const list = Array.from(selectedList)
    const spaceLeft = maxFiles - files.length

    if (spaceLeft <= 0) {
      setErrorMessage(`Maximum upload limit reached (${maxFiles} images max).`)
      return
    }

    const validFiles: File[] = []
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

    for (let i = 0; i < Math.min(list.length, spaceLeft); i++) {
      const file = list[i]

      // 1. Format validation
      if (!allowedTypes.includes(file.type)) {
        setErrorMessage('Unsupported file format. Please upload JPEG, PNG, WEBP, or GIF.')
        continue
      }

      // 2. Size validation
      if (file.size > maxSizeMB * 1024 * 1024) {
        setErrorMessage(`File too large. Max size allowed is ${maxSizeMB}MB.`)
        continue
      }

      validFiles.push(file)
    }

    if (validFiles.length === 0) return

    // Create uploaded files models
    const newFiles: UploadedFile[] = validFiles.map((file) => ({
      id: 'img_' + Math.random().toString(36).substr(2, 9),
      name: file.name,
      url: URL.createObjectURL(file),
      size: file.size,
      progress: 0,
      status: 'uploading'
    }))

    setFiles((prev) => [...prev, ...newFiles])

    // Simulate upload progress for each new file
    newFiles.forEach((fileModel) => {
      simulateUpload(fileModel.id)
    })
  }

  const simulateUpload = (id: string) => {
    let currentProgress = 0
    const interval = setInterval(() => {
      currentProgress += Math.floor(Math.random() * 15) + 5
      if (currentProgress >= 100) {
        currentProgress = 100
        clearInterval(interval)
        setFiles((prev) =>
          prev.map((f) =>
            f.id === id ? { ...f, progress: 100, status: 'success' } : f
          )
        )
      } else {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === id ? { ...f, progress: currentProgress } : f
          )
        )
      }
    }, 120)
  }

  // Remove File
  const handleRemoveFile = (idToRemove: string) => {
    setFiles((prev) => {
      const target = prev.find((f) => f.id === idToRemove)
      if (target && target.url.startsWith('blob:')) {
        URL.revokeObjectURL(target.url)
      }
      return prev.filter((f) => f.id !== idToRemove)
    })
    setErrorMessage(null)
  }

  // Replace File Trigger
  const handleReplaceFile = (idToReplace: string) => {
    // We remove the old one first, and then open the file input
    handleRemoveFile(idToReplace)
    fileInputRef.current?.click()
  }

  // Camera capture methods
  const startCamera = async () => {
    setErrorMessage(null)
    setIsCameraActive(true)
    setCameraSupported(true)

    if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraSupported(false)
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      setCameraStream(stream)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      console.error('Camera access error:', err)
      setCameraSupported(false)
    }
  }

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop())
      setCameraStream(null)
    }
    setIsCameraActive(false)
  }

  const capturePhoto = () => {
    if (!cameraSupported) {
      // Simulate taking a photo if webcam is unavailable
      simulateCapture()
      return
    }

    const video = videoRef.current
    const canvas = canvasRef.current

    if (video && canvas) {
      const context = canvas.getContext('2d')
      if (context) {
        canvas.width = video.videoWidth || 640
        canvas.height = video.videoHeight || 480
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        canvas.toBlob((blob) => {
          if (blob) {
            const file = new File([blob], `capture_${Date.now()}.jpg`, { type: 'image/jpeg' })
            const url = URL.createObjectURL(file)
            const newFile: UploadedFile = {
              id: 'img_' + Math.random().toString(36).substr(2, 9),
              name: file.name,
              url,
              size: file.size,
              progress: 100,
              status: 'success'
            }
            setFiles((prev) => [...prev, newFile])
            stopCamera()
          }
        }, 'image/jpeg', 0.95)
      }
    }
  }

  // Simulate snapshot for unsupported browsers or missing camera permissions
  const simulateCapture = () => {
    const newFile: UploadedFile = {
      id: 'img_' + Math.random().toString(36).substr(2, 9),
      name: `simulated_capture_${Date.now()}.jpg`,
      // Standard inline gradient image representation (SVG)
      url: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%234f46e5"/><stop offset="100%" stop-color="%2306b6d4"/></linearGradient></defs><rect width="600" height="400" fill="url(%23g)"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="white">📷 Camera Snapshot Simulator</text></svg>',
      size: 45000,
      progress: 100,
      status: 'success'
    }

    setFiles((prev) => [...prev, newFile])
    stopCamera()
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="multimodal-upload-card">
      <div className="multimodal-header">
        <h3>🖼️ Image Upload & Camera Capture</h3>
        <p className="muted text-xs">
          Upload up to {maxFiles} images (Max size: {maxSizeMB}MB each) for prompt context.
        </p>
      </div>

      {errorMessage && (
        <div className="status-banner error upload-error">
          ⚠️ {errorMessage}
        </div>
      )}

      {/* Main Drag & Drop Zone */}
      {!isCameraActive ? (
        <div
          className={`image-dropzone ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            multiple
            accept="image/*"
            style={{ display: 'none' }}
          />
          <div className="dropzone-icon">☁️</div>
          <h4>Drag & Drop your images here</h4>
          <p className="muted text-xs">or click to browse local files</p>
          
          <div className="dropzone-actions">
            <button
              type="button"
              className="ghost-button camera-trigger-btn"
              onClick={(e) => {
                e.stopPropagation()
                startCamera()
              }}
            >
              📷 Use Camera
            </button>
          </div>
        </div>
      ) : (
        /* Camera capture drawer viewport */
        <div className="camera-viewport-card">
          <div className="camera-frame">
            {cameraSupported ? (
              <video ref={videoRef} autoPlay playsInline muted />
            ) : (
              <div className="camera-unsupported-preview">
                <span>📷</span>
                <p>Webcam stream blocked or not supported in this browser.</p>
                <p className="muted text-xs">Click "Capture" to use a simulated snapshot image.</p>
              </div>
            )}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </div>

          <div className="camera-controls">
            <Button onClick={capturePhoto} variant="primary">
              📸 Capture Photo
            </Button>
            <Button onClick={stopCamera} variant="secondary">
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Uploaded File Previews */}
      {files.length > 0 && (
        <div className="image-previews-tray">
          <h4>Uploaded Attachments:</h4>
          <div className="image-previews-grid">
            {files.map((file) => {
              const isUploading = file.status === 'uploading'
              return (
                <div key={file.id} className="image-preview-card">
                  <div className="preview-thumbnail">
                    <img src={file.url} alt={file.name} />
                    {isUploading && (
                      <div className="upload-loading-overlay">
                        <div className="upload-spinner" />
                        <span className="progress-num">{file.progress}%</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="preview-details">
                    <span className="file-name" title={file.name}>
                      {file.name}
                    </span>
                    <span className="file-size">{formatSize(file.size)}</span>
                    
                    {isUploading ? (
                      <div className="preview-progress-track">
                        <div
                          className="preview-progress-fill"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                    ) : (
                      <div className="preview-actions">
                        <button
                          type="button"
                          className="preview-action-btn replace"
                          onClick={() => handleReplaceFile(file.id)}
                        >
                          🔄 Replace
                        </button>
                        <button
                          type="button"
                          className="preview-action-btn remove"
                          onClick={() => handleRemoveFile(file.id)}
                        >
                          🗑️ Remove
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
