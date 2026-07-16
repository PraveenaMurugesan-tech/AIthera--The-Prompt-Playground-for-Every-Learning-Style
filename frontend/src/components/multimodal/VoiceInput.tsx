import { useEffect, useState, useRef } from 'react'

type VoiceInputProps = {
  onTranscript: (text: string) => void
  placeholder?: string
  buttonOnly?: boolean
}

export const VoiceInput = ({ onTranscript, placeholder = 'Speak now to transcribe...', buttonOnly = false }: VoiceInputProps) => {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSupported, setIsSupported] = useState(true)
  const [showSimulator, setShowSimulator] = useState(false)

  const recognitionRef = useRef<any>(null)

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      setIsSupported(false)
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsRecording(true)
      setError(null)
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error: ', event.error)
      if (event.error === 'not-allowed') {
        setError('Microphone permission denied. Please enable microphone access in your browser settings.')
      } else if (event.error === 'no-speech') {
        // Safe to ignore or guide user
      } else {
        setError(`Speech error: ${event.error}`)
      }
      setIsRecording(false)
    }

    recognition.onend = () => {
      setIsRecording(false)
    }

    recognition.onresult = (event: any) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript
        } else {
          interimTranscript += event.results[i][0].transcript
        }
      }

      const activeText = finalTranscript || interimTranscript
      setTranscript(activeText)
      if (finalTranscript) {
        onTranscript(finalTranscript)
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [onTranscript])

  const startRecording = () => {
    setError(null)
    setTranscript('')
    if (!isSupported) {
      setShowSimulator(true)
      setIsRecording(true)
      simulateSpeech()
      return
    }

    try {
      recognitionRef.current?.start()
    } catch (err) {
      console.error('Start error:', err)
      setError('Could not initialize microphone. Please refresh and try again.')
    }
  }

  const stopRecording = () => {
    if (!isSupported) {
      setIsRecording(false)
      return
    }
    try {
      recognitionRef.current?.stop()
    } catch (err) {
      console.error('Stop error:', err)
    }
  }

  // Simulation fallback for unsupported browsers / environments
  const simulateSpeech = () => {
    const simulationTexts = [
      'Show me how to construct a visual concepts map for React lifecycle hooks.',
      'Explain the difference between a state and a prop in simple terms.',
      'Create an intermediate multiple choice quiz testing python decorators.',
      'Provide step-by-step instructions on designing a responsive dashboard with CSS.'
    ]
    const chosenText = simulationTexts[Math.floor(Math.random() * simulationTexts.length)]
    
    // Simulate typing transcription effect
    let currentIdx = 0
    const interval = setInterval(() => {
      if (currentIdx < chosenText.length) {
        setTranscript(prev => prev + chosenText.charAt(currentIdx))
        currentIdx++
      } else {
        clearInterval(interval)
        setIsRecording(false)
        onTranscript(chosenText)
      }
    }, 45)
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  if (buttonOnly) {
    return (
      <div className="voice-input-inline-shell">
        <button
          type="button"
          className={`icon-button mic-inline-btn ${isRecording ? 'recording-active' : ''}`}
          onClick={toggleRecording}
          title={isRecording ? 'Stop recording voice' : 'Start recording voice'}
        >
          {isRecording ? '🔴' : '🎤'}
        </button>
        {isRecording && (
          <div className="inline-wave-overlay">
            <span className="inline-wave-dot" />
            <span className="inline-wave-dot" />
            <span className="inline-wave-dot" />
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="voice-input-card">
      <div className="voice-header-row">
        <h3>🎙️ Speech-to-Text Recorder</h3>
        {!isSupported && (
          <span className="unsupported-warning-badge">⚠️ Simulated Mode Active</span>
        )}
      </div>

      {error && (
        <div className="status-banner error voice-error">
          {error}
        </div>
      )}

      <div className="voice-recorder-core">
        <button
          type="button"
          className={`voice-mic-circle ${isRecording ? 'recording' : ''}`}
          onClick={toggleRecording}
          aria-label={isRecording ? 'Stop voice recording' : 'Start voice recording'}
        >
          <span className="mic-symbol">🎤</span>
          {isRecording && <span className="mic-ring-pulse" />}
        </button>

        <div className="voice-recorder-status">
          <h4>{isRecording ? 'Listening...' : 'Ready to record'}</h4>
          <p className="muted text-xs">
            {isRecording ? 'Speak clearly into your microphone.' : 'Click the microphone button to dictate.'}
          </p>
        </div>
      </div>

      {isRecording && (
        <div className="voice-wave-container">
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
          <div className="wave-bar" />
        </div>
      )}

      {(transcript || isRecording) && (
        <div className="voice-transcript-preview">
          <h5>Live Preview:</h5>
          <p className={transcript ? 'text-preview' : 'text-preview empty'}>
            {transcript || placeholder}
          </p>
        </div>
      )}

      {!isSupported && showSimulator && (
        <div className="status-banner success voice-sim-info">
          💡 Simulated a user voice input for browser compatibility.
        </div>
      )}
    </div>
  )
}
