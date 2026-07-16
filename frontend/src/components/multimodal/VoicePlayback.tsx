import { useEffect, useState, useRef } from 'react'

type VoicePlaybackProps = {
  text: string
  buttonOnly?: boolean
}

export const VoicePlayback = ({ text, buttonOnly = false }: VoicePlaybackProps) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([])
  
  // Voice preferences
  const [selectedVoiceName, setSelectedVoiceName] = useState<string>(() => {
    return localStorage.getItem('aithera_voice_name') || ''
  })
  const [rate, setRate] = useState<number>(() => {
    const val = localStorage.getItem('aithera_voice_rate')
    return val ? parseFloat(val) : 1.0
  })
  const [pitch, setPitch] = useState<number>(() => {
    const val = localStorage.getItem('aithera_voice_pitch')
    return val ? parseFloat(val) : 1.0
  })

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Load system voices
  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return

    const loadVoices = () => {
      const allVoices = window.speechSynthesis.getVoices()
      // Filter unique voices and keep only english or common readable ones for simplicity
      setVoices(allVoices)
      
      // Default selection if none saved
      if (!localStorage.getItem('aithera_voice_name') && allVoices.length > 0) {
        // Try to find a google english or default voice
        const defaultVoice = allVoices.find(v => v.lang.includes('en') || v.default) || allVoices[0]
        setSelectedVoiceName(defaultVoice.name)
      }
    }

    loadVoices()
    window.speechSynthesis.onvoiceschanged = loadVoices
  }, [])

  // Clean synthesis when text changes or component unmounts
  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [text])

  const handlePlay = () => {
    if (!window.speechSynthesis) {
      alert('Speech Synthesis API is not supported in this browser.')
      return
    }

    if (isPaused) {
      window.speechSynthesis.resume()
      setIsPaused(false)
      setIsPlaying(true)
      return
    }

    // Cancel any active speech
    window.speechSynthesis.cancel()

    // Clean text: strip markdown elements for clearer reading voice
    const cleanText = text
      .replace(/[#*`_>]/g, '') // remove markdown symbols
      .replace(/\[.*\]\(.*\)/g, '') // remove markdown links

    const utterance = new SpeechSynthesisUtterance(cleanText)
    
    // Configure voice properties
    const activeVoice = voices.find(v => v.name === selectedVoiceName)
    if (activeVoice) {
      utterance.voice = activeVoice
    }
    
    utterance.rate = rate
    utterance.pitch = pitch

    utterance.onend = () => {
      setIsPlaying(false)
      setIsPaused(false)
    }

    utterance.onerror = (e) => {
      console.error('Synthesis error:', e)
      setIsPlaying(false)
      setIsPaused(false)
    }

    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
    setIsPlaying(true)
    setIsPaused(false)
  }

  const handlePause = () => {
    if (window.speechSynthesis && isPlaying) {
      window.speechSynthesis.pause()
      setIsPaused(true)
      setIsPlaying(false)
    }
  }

  const handleStop = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      setIsPlaying(false)
      setIsPaused(false)
    }
  }

  const handleSavePref = (key: 'name' | 'rate' | 'pitch', value: any) => {
    if (key === 'name') {
      setSelectedVoiceName(value)
      localStorage.setItem('aithera_voice_name', value)
    } else if (key === 'rate') {
      setRate(value)
      localStorage.setItem('aithera_voice_rate', value.toString())
    } else if (key === 'pitch') {
      setPitch(value)
      localStorage.setItem('aithera_voice_pitch', value.toString())
    }

    // If speaking, restart to apply new voice configuration
    if (isPlaying || isPaused) {
      setTimeout(() => handlePlay(), 100)
    }
  }

  if (buttonOnly) {
    return (
      <div className="voice-playback-inline-shell">
        {!isPlaying ? (
          <button
            type="button"
            className="bubble-action-btn playback-btn"
            onClick={handlePlay}
            title="Read aloud"
          >
            🔊 Read
          </button>
        ) : (
          <div className="inline-playback-controls">
            <button
              type="button"
              className="bubble-action-btn playback-btn active"
              onClick={handlePause}
              title="Pause reading"
            >
              ⏸️ Pause
            </button>
            <button
              type="button"
              className="bubble-action-btn playback-btn"
              onClick={handleStop}
              title="Stop reading"
            >
              ⏹️ Stop
            </button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="voice-playback-card">
      <h3>🔊 Text-to-Speech Playback</h3>
      <p className="muted text-xs">Listen to instructions, responses, or prompts read aloud.</p>

      {/* Playback status display */}
      <div className="playback-status-monitor">
        {isPlaying ? (
          <div className="status-indicator-active">
            <span className="speaker-wave-animation">🔊</span> Speaking...
          </div>
        ) : isPaused ? (
          <div className="status-indicator-paused">⏸️ Paused</div>
        ) : (
          <div className="status-indicator-idle">⏹️ Ready to read</div>
        )}
      </div>

      {/* Main playback control bar */}
      <div className="playback-controls-row">
        <button
          type="button"
          className="playback-control-btn play"
          onClick={handlePlay}
          disabled={!text}
          title="Play reading"
        >
          ▶️ Play
        </button>
        <button
          type="button"
          className="playback-control-btn pause"
          onClick={handlePause}
          disabled={!isPlaying}
          title="Pause reading"
        >
          ⏸️ Pause
        </button>
        <button
          type="button"
          className="playback-control-btn stop"
          onClick={handleStop}
          disabled={!isPlaying && !isPaused}
          title="Stop reading"
        >
          ⏹️ Stop
        </button>
      </div>

      {/* Settings Panel */}
      <div className="voice-settings-panel">
        <h4>⚙️ Voice Configurations</h4>

        <div className="settings-field-col">
          <label>
            <span>Voice Profile:</span>
            <select
              value={selectedVoiceName}
              onChange={(e) => handleSavePref('name', e.target.value)}
            >
              {voices.map((v) => (
                <option key={v.name} value={v.name}>
                  {v.name} ({v.lang})
                </option>
              ))}
              {voices.length === 0 && (
                <option value="">Default Browser Voice</option>
              )}
            </select>
          </label>
        </div>

        <div className="settings-sliders-row">
          <label className="slider-field">
            <span>Speed ({rate}x):</span>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={rate}
              onChange={(e) => handleSavePref('rate', parseFloat(e.target.value))}
            />
          </label>

          <label className="slider-field">
            <span>Pitch ({pitch}):</span>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={pitch}
              onChange={(e) => handleSavePref('pitch', parseFloat(e.target.value))}
            />
          </label>
        </div>
      </div>
    </div>
  )
}
