import { useMemo, useState, type ChangeEvent, type FormEvent } from 'react'
import { Button } from '../../components/common/Button'
import { Card } from '../../components/common/Card'
import { generateLearningPrompt, type PromptFormat } from '../../services/api'
import { useToast } from '../../context/ToastContext'

type WorkspaceFormState = {
  topic: string
  learningStyle: 'adaptive' | 'visual' | 'step_by_step' | 'conversational' | 'exam_focused'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  format: PromptFormat
}

type PromptResult = {
  title: string
  summary: string
  content: string
  badge: string
}

const initialFormState: WorkspaceFormState = {
  topic: '',
  learningStyle: 'adaptive',
  difficulty: 'intermediate',
  format: 'notes',
}

interface ISpeechRecognitionEvent {
  resultIndex: number
  results: {
    length: number
    [index: number]: {
      isFinal: boolean
      [index: number]: {
        transcript: string
      }
    }
  }
}

interface ISpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  onresult: ((event: ISpeechRecognitionEvent) => void) | null
  onerror: ((event: Event) => void) | null
  onend: ((event: Event) => void) | null
  start(): void
  stop(): void
}

interface WindowWithSpeech extends Window {
  SpeechRecognition?: new () => ISpeechRecognition
  webkitSpeechRecognition?: new () => ISpeechRecognition
}

export const WorkspacePage = () => {
  const { showToast, dismissToast } = useToast()
  const [form, setForm] = useState<WorkspaceFormState>(initialFormState)
  const [imageData, setImageData] = useState<string | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [result, setResult] = useState<PromptResult | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = <K extends keyof WorkspaceFormState>(field: K, value: WorkspaceFormState[K]) => {
    setForm((current) => ({ ...current, [field]: value }))
    if (error) {
      setError(null)
    }
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!form.topic.trim()) {
      setError('Please enter a topic or search term to generate a prompt.')
      return
    }

    setIsGenerating(true)
    setError(null)
    let toastId = ''

    try {
      toastId = showToast('Consulting AI Council & refining prompt...', 'loading', 0)
      const generated = await generateLearningPrompt(
        {
          topic: form.topic.trim() || 'Analyze attached image',
          learningStyle: form.learningStyle,
          difficulty: form.difficulty,
          format: form.format,
          imageData: imageData || undefined,
        }
      )

      setResult(generated)
      dismissToast(toastId)
      showToast('Consensus prompt ready!', 'success')

      // Save local storage history cache to synchronize with Phase 8 history module
      try {
        const newHistoryItem = {
          id: Date.now(),
          user_id: 1,
          topic: form.topic.trim(),
          learning_style: form.learningStyle,
          difficulty: form.difficulty,
          generated_prompt: generated.content,
          created_at: new Date().toISOString()
        }
        const currentHistory = localStorage.getItem('aithera_prompt_history')
        const parsedHistory = currentHistory ? JSON.parse(currentHistory) : []
        localStorage.setItem('aithera_prompt_history', JSON.stringify([newHistoryItem, ...parsedHistory]))
      } catch (err) {
        console.error('Failed to update local prompt history backup:', err)
      }
    } catch (requestError) {
      if (toastId) dismissToast(toastId)
      showToast('Failed to generate prompt.', 'error')
      setError(requestError instanceof Error ? requestError.message : 'Unable to generate a prompt right now.')
      setResult(null)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleImageUpload = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.size > 4 * 1024 * 1024) {
        showToast('Image must be less than 4MB', 'error')
        return
      }
      const reader = new FileReader()
      reader.onload = (e) => {
        setImageData(e.target?.result as string)
        if (!form.topic) {
          setForm(prev => ({ ...prev, topic: 'Analyze attached image' }))
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false)
      // Stop logic will go here in actual implementation
      return
    }

    const win = window as unknown as WindowWithSpeech
    if (!win.SpeechRecognition && !win.webkitSpeechRecognition) {
      showToast('Speech recognition not supported in this browser.', 'error')
      return
    }

    const SpeechRecognition = win.SpeechRecognition || win.webkitSpeechRecognition
    if (!SpeechRecognition) return

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event: ISpeechRecognitionEvent) => {
      let finalTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript
        }
      }
      if (finalTranscript) {
        setForm(prev => ({ ...prev, topic: prev.topic + ' ' + finalTranscript.trim() }))
      }
    }

    recognition.onerror = () => {
      setIsRecording(false)
      showToast('Voice recognition failed.', 'error')
    }

    recognition.onend = () => {
      setIsRecording(false)
    }

    recognition.start()
    setIsRecording(true)
    showToast('Listening...', 'success')
  }

  const helperText = useMemo(() => {
    return `Tailored for ${form.learningStyle.replace(/_/g, ' ')} learners at ${form.difficulty} difficulty.`
  }, [form.difficulty, form.learningStyle])

  return (
    <div className="workspace-page">
      <Card title="AI Learning Workspace" subtitle="Generate personalized prompts tailored to your learning style using AI Council.">
        <div className="workspace-hero">
          <div className="workspace-hero-badge">🟢 AI Council Ready</div>
          <p className="muted">All AI providers are online and available for your next learning session.</p>
        </div>
        <form className="workspace-form" onSubmit={handleSubmit}>
          <label className="field field-search">
            <span>📚 Topic</span>
            <div className="input-icon-shell">
              <span className="input-icon">✦</span>
              <input
                value={form.topic}
                placeholder="What would you like to learn today?"
                onChange={(event: ChangeEvent<HTMLInputElement>) => handleChange('topic', event.target.value)}
                style={{ flex: 1 }}
              />
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', paddingRight: '8px' }}>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center' }}>
                  <span title="Attach Image">📎</span>
                  <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleImageUpload} />
                </label>
                <button 
                  type="button" 
                  onClick={toggleRecording} 
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: isRecording ? 'red' : 'inherit' }}
                  title="Voice dictation"
                >
                  🎙️
                </button>
              </div>
            </div>
            {imageData && (
              <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--primary-color)' }}>
                ✓ Image attached ({Math.round(imageData.length / 1024)} KB)
                <button type="button" onClick={() => setImageData(null)} style={{ marginLeft: '8px', background: 'none', border: 'none', color: 'red', cursor: 'pointer' }}>Remove</button>
              </div>
            )}
          </label>

          <div className="workspace-form-grid">
            <label className="field">
              <span>🧠 Learning Style</span>
              <select value={form.learningStyle} onChange={(event: ChangeEvent<HTMLSelectElement>) => handleChange('learningStyle', event.target.value as WorkspaceFormState['learningStyle'])}>
                <option value="adaptive">Adaptive</option>
                <option value="visual">Visual</option>
                <option value="step_by_step">Step by step</option>
                <option value="conversational">Conversational</option>
                <option value="exam_focused">Exam focused</option>
              </select>
            </label>

            <label className="field">
              <span>🎯 Difficulty</span>
              <select value={form.difficulty} onChange={(event: ChangeEvent<HTMLSelectElement>) => handleChange('difficulty', event.target.value as WorkspaceFormState['difficulty'])}>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </label>
          </div>

          <label className="field">
            <span>📄 Prompt Format</span>
            <select value={form.format} onChange={(event: ChangeEvent<HTMLSelectElement>) => handleChange('format', event.target.value as PromptFormat)}>
              <option value="notes">Notes</option>
              <option value="quiz">Quiz</option>
              <option value="explanation">Explanation</option>
              <option value="flashcards">Flashcards</option>
            </select>
          </label>

          <div className="workspace-actions">
            <Button type="submit" disabled={isGenerating}>
              {isGenerating ? 'Generating…' : '✨ Generate Personalized Prompt'}
            </Button>
            <p className="muted">{helperText}</p>
          </div>
        </form>
      </Card>

      <div className="workspace-status-grid">
        <Card title="AI Council Status" subtitle="Live provider availability">
          <div className="status-stack">
            <div className="status-pill-row"><span>GPT</span><span className="status-online">● Online</span></div>
            <div className="status-pill-row"><span>Claude</span><span className="status-online">● Online</span></div>
            <div className="status-pill-row"><span>Gemini</span><span className="status-online">● Online</span></div>
            <div className="status-pill-row"><span>DeepSeek</span><span className="status-online">● Online</span></div>
            <div className="status-divider" />
            <div className="status-pill-row"><span>Consensus Engine</span><strong>Ready</strong></div>
            <div className="status-pill-row"><span>Confidence</span><strong>94%</strong></div>
          </div>
        </Card>
        <Card title="Generated Prompt" subtitle="Your personalized response will appear here.">
          {error ? <div className="status-banner error">{error}</div> : null}
          {isGenerating ? (
            <div className="workspace-loading">
              <div className="loading-orb" aria-hidden="true">
                <div className="loading-orb-core" />
              </div>
              <div>
                <h4>Crafting your prompt</h4>
                <p className="muted">The AI council is shaping a response that matches your learning style…</p>
              </div>
            </div>
          ) : result ? (
            <div className="prompt-chat-layout">
              <div className="prompt-bubble prompt-bubble-user">
                <span className="summary-label">Request</span>
                <p>{form.topic}</p>
              </div>
              <div className="prompt-bubble prompt-bubble-ai">
                <div className="prompt-bubble-header">
                  <strong>{result.title}</strong>
                  <span className="prompt-badge">{result.badge}</span>
                </div>
                <p>{result.summary}</p>
                <div className="prompt-output">{result.content}</div>
              </div>
            </div>
          ) : (
            <div className="workspace-empty-state">
              <div className="empty-state-icon">☁️</div>
              <h4>Start a learning session</h4>
              <p className="muted">Choose a topic, pick a learning style, and generate a prompt that fits your pace.</p>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
