import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/common/Card'
import { Button } from '../../components/common/Button'
import { VoiceInput } from '../../components/multimodal/VoiceInput'
import { VoicePlayback } from '../../components/multimodal/VoicePlayback'

export const VoicePage = () => {
  const navigate = useNavigate()
  const [promptDraft, setPromptDraft] = useState('')
  const [copied, setCopied] = useState(false)

  const handleTranscriptReceived = (text: string) => {
    setPromptDraft((prev) => {
      const separator = prev ? ' ' : ''
      return prev + separator + text
    })
  }

  const handleSendToChat = () => {
    if (!promptDraft.trim()) return
    navigate('/chat', {
      state: {
        initialPrompt: promptDraft,
        topic: 'Voice dictated topic',
        learningStyle: 'conversational',
        difficulty: 'intermediate'
      }
    })
  }

  const handleSendToWorkspace = () => {
    if (!promptDraft.trim()) return
    navigate('/workspace', {
      state: {
        prefilledTopic: promptDraft,
        prefilledStyle: 'conversational'
      }
    })
  }

  const handleCopyDraft = async () => {
    if (!promptDraft) return
    try {
      await navigator.clipboard.writeText(promptDraft)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  return (
    <div className="multimodal-page-container">
      <div className="multimodal-page-header">
        <h1>🎤 Multimodal Voice Playground</h1>
        <p className="muted">
          Speak to dictate your learning prompts and configure natural audio playback options.
        </p>
      </div>

      <div className="multimodal-page-grid">
        {/* Left column - Speech to text recorder */}
        <div className="upload-section-col">
          <Card>
            <VoiceInput onTranscript={handleTranscriptReceived} />
          </Card>
        </div>

        {/* Right column - Draft prompt and Text to Speech playback controls */}
        <div className="analysis-section-col">
          <Card title="Voice Draft Space" subtitle="Review your dictated text and listen to audio feedback.">
            <div className="voice-draft-workspace animate-fade-in">
              <label className="field">
                <span>📝 Prompt Draft Text:</span>
                <textarea
                  value={promptDraft}
                  onChange={(e) => setPromptDraft(e.target.value)}
                  placeholder="Record your voice or type your prompt here to listen or dispatch..."
                  rows={6}
                  style={{
                    borderRadius: '0.85rem',
                    padding: '0.8rem',
                    border: '1px solid rgba(148, 163, 184, 0.45)',
                    fontFamily: 'inherit',
                    lineHeight: '1.45',
                    width: '100%',
                    resize: 'vertical'
                  }}
                />
              </label>

              <div className="draft-actions-bar" style={{ marginTop: '0.5rem', display: 'flex', gap: '0.55rem' }}>
                <Button
                  onClick={() => setPromptDraft('')}
                  variant="secondary"
                  disabled={!promptDraft}
                  style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                >
                  🧹 Clear Draft
                </Button>
                <Button
                  onClick={handleCopyDraft}
                  variant="secondary"
                  disabled={!promptDraft}
                  style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
                >
                  {copied ? '✅ Copied!' : '📋 Copy Draft'}
                </Button>
              </div>

              {/* TTS Readback Module */}
              <div className="tts-container" style={{ marginTop: '1.5rem', borderTop: '1px solid rgba(148, 163, 184, 0.16)', paddingTop: '1.25rem' }}>
                <VoicePlayback text={promptDraft} />
              </div>

              {/* Dispatch Controls */}
              <div className="voice-dispatch-actions" style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <Button
                  onClick={handleSendToChat}
                  variant="primary"
                  disabled={!promptDraft.trim()}
                >
                  💬 Send to Chat
                </Button>
                <Button
                  onClick={handleSendToWorkspace}
                  variant="secondary"
                  disabled={!promptDraft.trim()}
                >
                  ✨ Send to Workspace
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
export default VoicePage
