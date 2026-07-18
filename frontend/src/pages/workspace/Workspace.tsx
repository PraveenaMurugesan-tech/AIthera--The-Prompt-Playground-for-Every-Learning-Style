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

export const WorkspacePage = () => {
  const { showToast, dismissToast } = useToast()
  const [form, setForm] = useState<WorkspaceFormState>(initialFormState)
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
          topic: form.topic.trim(),
          learningStyle: form.learningStyle,
          difficulty: form.difficulty,
          format: form.format,
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
              />
            </div>
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
