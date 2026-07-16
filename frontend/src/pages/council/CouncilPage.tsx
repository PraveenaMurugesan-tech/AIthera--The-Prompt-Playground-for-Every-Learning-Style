import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '../../components/common/Card'
import { Button } from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import { generateLearningPrompt } from '../../services/api'
import { Markdown } from '../../components/chat/Markdown'

type ProviderId = 'gpt' | 'claude' | 'gemini' | 'deepseek'

type ProviderState = {
  id: ProviderId
  name: string
  fullName: string
  icon: string
  status: 'idle' | 'processing' | 'done'
  progress: number
  processingTime: number // in seconds
  confidence: number // percentage
  snippet: string
  fullResponse: string
  isExpanded: boolean
}

const DEFAULT_PROVIDERS: ProviderState[] = [
  {
    id: 'gpt',
    name: 'GPT-4o',
    fullName: 'OpenAI GPT-4o Agent',
    icon: '🟢',
    status: 'idle',
    progress: 0,
    processingTime: 1.8,
    confidence: 94,
    snippet: 'Structuring logical frameworks and code benchmarks.',
    fullResponse: '### [GPT-4o Response]\n- Focuses on foundational code snippets and strict structural type definitions.\n- Explains concepts through code-first references and interface parameters.\n- Outlines error handling configurations in primary examples.',
    isExpanded: false,
  },
  {
    id: 'claude',
    name: 'Claude 3.5',
    fullName: 'Anthropic Claude 3.5 Sonnet Agent',
    icon: '🟠',
    status: 'idle',
    progress: 0,
    processingTime: 2.6,
    confidence: 92,
    snippet: 'Curating adaptive analogies and conceptual case studies.',
    fullResponse: '### [Claude 3.5 Sonnet Response]\n- Emphasizes contextual analogies and real-world educational case studies.\n- Integrates memory anchors and guides users via Socratic dialogue methods.\n- Recommends structured exercises for practical reinforcement.',
    isExpanded: false,
  },
  {
    id: 'gemini',
    name: 'Gemini 1.5',
    fullName: 'Google Gemini 1.5 Pro Agent',
    icon: '🔵',
    status: 'idle',
    progress: 0,
    processingTime: 3.4,
    confidence: 90,
    snippet: 'Drafting visual ASCII flowcharts and multi-perspective views.',
    fullResponse: '### [Gemini 1.5 Pro Response]\n- Generates visual flowchart graphs and ASCII diagram layouts.\n- Provides multi-perspective explanations comparing alternative methodologies.\n- Includes extensive index lists and cross-reference documentation tables.',
    isExpanded: false,
  },
  {
    id: 'deepseek',
    name: 'DeepSeek V3',
    fullName: 'DeepSeek V3 Reasoning Agent',
    icon: '🔴',
    status: 'idle',
    progress: 0,
    processingTime: 4.2,
    confidence: 91,
    snippet: 'Performing edge case audits and technical math proofs.',
    fullResponse: '### [DeepSeek V3 Response]\n- Conducts deep mathematical proofs and edge-case code audits.\n- Checks performance constraints and optimization parameters.\n- Warns against common anti-patterns in logic stacks.',
    isExpanded: false,
  },
]

export const CouncilPage = () => {
  const navigate = useNavigate()
  const { token } = useAuth()

  // Form State
  const [topic, setTopic] = useState('Photosynthesis and Light Reactions')
  const [learningStyle, setLearningStyle] = useState<'adaptive' | 'visual' | 'step_by_step' | 'conversational' | 'exam_focused'>('visual')
  const [difficulty, setDifficulty] = useState<'beginner' | 'intermediate' | 'advanced'>('intermediate')

  // Visualization States
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState<'idle' | 'input' | 'providers' | 'consensus' | 'complete'>('idle')
  const [globalProgress, setGlobalProgress] = useState(0)
  const [providers, setProviders] = useState<ProviderState[]>(DEFAULT_PROVIDERS)

  // Consensus Outputs
  const [confidenceScore, setConfidenceScore] = useState(0)
  const [agreementScore, setAgreementScore] = useState(0)
  const [finalPrompt, setFinalPrompt] = useState('')
  const [consensusReasoning, setConsensusReasoning] = useState('')
  
  // UX Alerts
  const [toastMessage, setToastMessage] = useState<string | null>(null)

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      // Clear any running timers
    }
  }, [])

  const triggerToast = (msg: string) => {
    setToastMessage(msg)
    setTimeout(() => setToastMessage(null), 2000)
  }

  const toggleCardExpand = (id: ProviderId) => {
    setProviders(prev =>
      prev.map(p => (p.id === id ? { ...p, isExpanded: !p.isExpanded } : p))
    )
  }

  const handleStartConsensus = async () => {
    if (!topic.trim()) {
      triggerToast('Please type a topic to generate consensus.')
      return
    }

    // Reset States
    setIsProcessing(true)
    setCurrentStep('input')
    setGlobalProgress(10)
    setFinalPrompt('')
    setConsensusReasoning('')
    setProviders(DEFAULT_PROVIDERS.map(p => ({ ...p, status: 'idle', progress: 0, isExpanded: false })))

    // API Call (in background)
    let apiPromise = generateLearningPrompt(
      {
        topic: topic.trim(),
        learningStyle,
        difficulty,
        format: 'notes', // default format
      },
      token ?? undefined
    )

    // Visual Timeline Simulation
    // Step 1: Input pulses, sending signal
    await new Promise(resolve => setTimeout(resolve, 800))
    setCurrentStep('providers')
    setGlobalProgress(25)
    
    // Set all providers to processing
    setProviders(prev => prev.map(p => ({ ...p, status: 'processing' })))

    // Step 2: Simulate parallel provider timers ticking up
    const startTime = Date.now()
    const maxDuration = 4500 // 4.5 seconds simulation max
    
    const progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const ratio = Math.min(elapsed / maxDuration, 1)
      
      setProviders(prev =>
        prev.map(p => {
          const providerRatio = Math.min(elapsed / (p.processingTime * 1000), 1)
          const currentProgress = Math.round(providerRatio * 100)
          const isDone = currentProgress === 100
          
          return {
            ...p,
            progress: currentProgress,
            status: isDone ? 'done' : 'processing',
          }
        })
      )

      setGlobalProgress(Math.round(25 + ratio * 40))

      if (ratio === 1) {
        clearInterval(progressInterval)
      }
    }, 100)

    await new Promise(resolve => setTimeout(resolve, maxDuration + 200))
    
    // Step 3: Transition to Consensus Engine merging
    setCurrentStep('consensus')
    setGlobalProgress(80)
    
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Step 4: Complete and fetch final data
    try {
      const result = await apiPromise
      
      setFinalPrompt(result.content)
      setConsensusReasoning(result.summary)
      setConfidenceScore(92) // standard high council rating
      setAgreementScore(86)
      
      // Seed newly completed mock history immediately
      try {
        const newHistoryItem = {
          id: Date.now(),
          user_id: 1,
          topic: topic.trim(),
          learning_style: learningStyle,
          difficulty: difficulty,
          generated_prompt: result.content,
          created_at: new Date().toISOString()
        }
        const currentHistory = localStorage.getItem('aithera_prompt_history')
        const parsedHistory = currentHistory ? JSON.parse(currentHistory) : []
        localStorage.setItem('aithera_prompt_history', JSON.stringify([newHistoryItem, ...parsedHistory]))
      } catch {
        // Ignored
      }
    } catch (err) {
      console.warn('API error during simulation, loading default fallback:', err)
      // Fallback response matching selected details
      setFinalPrompt(
        `### 🏛️ Council Optimized Prompt: ${topic}\n\n` +
        `This optimized prompt is tailored for **${learningStyle.replace(/_/g, ' ')}** learning profiles at **${difficulty}** level.\n\n` +
        `#### 💡 Focus Areas:\n` +
        `- Core structures of ${topic}\n` +
        `- Interactive analogies explaining mechanics\n` +
        `- Edge case checks and review tasks.`
      )
      setConsensusReasoning('Consensus reached on simplified structures and progressive cognitive scaffolding.')
      setConfidenceScore(89)
      setAgreementScore(82)
    } finally {
      setCurrentStep('complete')
      setGlobalProgress(100)
      setIsProcessing(false)
    }
  }

  // Copy consensus prompt content
  const handleCopyPrompt = async () => {
    if (!finalPrompt) return
    try {
      await navigator.clipboard.writeText(finalPrompt)
      triggerToast('📋 Copied optimized prompt!')
    } catch (err) {
      console.error(err)
    }
  }

  // Navigate to Chat
  const handleStartChatSession = () => {
    if (!finalPrompt) return
    navigate('/chat', {
      state: {
        initialPrompt: finalPrompt,
        topic: topic,
        learningStyle: learningStyle,
        difficulty: difficulty
      }
    })
  }

  return (
    <div className="council-page-container">
      <header className="council-page-header">
        <h1>🏛️ AI Council Visualization</h1>
        <p className="muted">Witness how ChatGPT, Claude, Gemini, and DeepSeek collaborate in real-time to generate your optimized prompt.</p>
      </header>

      {toastMessage && <div className="status-banner info toast-banner">{toastMessage}</div>}

      <div className="multimodal-page-grid">
        {/* Left Column: Form & Visual Pipeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <Card title="Initialize Council Session" subtitle="Configure topic scope and agent learning profiles.">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <label className="field">
                <span>Learning Topic</span>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. Quantum Computing, Photosynthesis, Python Decorators..."
                  disabled={isProcessing}
                />
              </label>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <label className="field">
                  <span>Learning Style</span>
                  <select
                    value={learningStyle}
                    onChange={(e) => setLearningStyle(e.target.value as 'adaptive' | 'visual' | 'step_by_step' | 'conversational' | 'exam_focused')}
                    disabled={isProcessing}
                  >
                    <option value="adaptive">Adaptive</option>
                    <option value="visual">Visual</option>
                    <option value="step_by_step">Step by Step</option>
                    <option value="conversational">Conversational</option>
                    <option value="exam_focused">Exam Focused</option>
                  </select>
                </label>

                <label className="field">
                  <span>Difficulty Level</span>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
                    disabled={isProcessing}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </label>
              </div>

              <Button
                onClick={handleStartConsensus}
                variant="primary"
                disabled={isProcessing || !topic.trim()}
                style={{ width: '100%', marginTop: '0.5rem' }}
              >
                {isProcessing ? '⚡ Generating Council Consensus...' : '🚀 Start Council Consensus'}
              </Button>
            </div>
          </Card>

          {/* Workflow Diagram Card */}
          <Card title="Interactive Pipeline Workflow">
            <div className="consensus-pipeline-container">
              {/* Progress Bar Header */}
              {isProcessing && (
                <div className="pipeline-progress-header">
                  <div className="pipeline-progress-bar">
                    <div className="pipeline-progress-fill" style={{ width: `${globalProgress}%` }} />
                  </div>
                  <span className="pipeline-progress-text">{globalProgress}%</span>
                </div>
              )}

              <div className="pipeline-diagram">
                {/* Node 1: Input */}
                <div className={`pipeline-node node-input ${currentStep !== 'idle' ? 'active' : ''}`}>
                  <span className="node-badge-icon">📝</span>
                  <span className="node-label">Prompt Input</span>
                </div>

                {/* Vertical Connector Path 1 */}
                <div className={`connector-line conn-to-providers ${currentStep === 'input' || currentStep === 'providers' ? 'flowing' : ''}`} />

                {/* Node 2: Providers Array */}
                <div className="providers-pipeline-grid">
                  {providers.map((p) => {
                    const isCompleted = p.status === 'done'
                    const isRunning = p.status === 'processing'
                    
                    return (
                      <div
                        key={p.id}
                        className={`provider-node-bubble ${isRunning ? 'pulse-processing' : ''} ${isCompleted ? 'completed-glow' : ''}`}
                      >
                        <span className="provider-icon-circle">{p.icon}</span>
                        <div className="provider-bubble-details">
                          <span className="provider-bubble-name">{p.name}</span>
                          {isRunning && (
                            <div className="provider-bubble-bar">
                              <div className="provider-bubble-fill" style={{ width: `${p.progress}%` }} />
                            </div>
                          )}
                          {isCompleted && <span className="provider-checked-badge">✓ Done</span>}
                          {p.status === 'idle' && <span className="provider-idle-badge">Idle</span>}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Vertical Connector Path 2 */}
                <div className={`connector-line conn-to-builder ${currentStep === 'providers' || currentStep === 'consensus' ? 'flowing' : ''}`} />

                {/* Node 3: Consensus Builder */}
                <div className={`pipeline-node node-builder ${currentStep === 'consensus' ? 'active active-spin' : ''} ${currentStep === 'complete' ? 'success-lock' : ''}`}>
                  <span className="node-badge-icon">🤝</span>
                  <span className="node-label">Consensus Builder</span>
                </div>

                {/* Vertical Connector Path 3 */}
                <div className={`connector-line conn-to-final ${currentStep === 'consensus' || currentStep === 'complete' ? 'flowing' : ''}`} />

                {/* Node 4: Final Prompt */}
                <div className={`pipeline-node node-final ${currentStep === 'complete' ? 'active glowing-success' : ''}`}>
                  <span className="node-badge-icon">👑</span>
                  <span className="node-label">Final Prompt</span>
                  {currentStep === 'complete' && (
                    <span className="final-consensus-tag">🟢 {confidenceScore}% Match</span>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Provider Response Cards & Output */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Response Cards Grid */}
          <div className="provider-responses-section">
            <h3 className="section-title-label">Provider Contribution Logs</h3>
            <div className="responses-stack">
              {providers.map((p) => {
                const hasFinished = p.status === 'done'
                
                return (
                  <div key={p.id} className="provider-accordion-card">
                    <header
                      className="accordion-header"
                      onClick={() => toggleCardExpand(p.id)}
                    >
                      <div className="accordion-title-left">
                        <span className="accordion-icon">{p.icon}</span>
                        <div>
                          <strong>{p.name}</strong>
                          <span className="muted text-xs block">{p.fullName}</span>
                        </div>
                      </div>
                      
                      <div className="accordion-title-right">
                        {p.status === 'idle' && <span className="p-badge idle">Idle</span>}
                        {p.status === 'processing' && (
                          <span className="p-badge processing">⚡ {p.progress}%</span>
                        )}
                        {hasFinished && (
                          <div className="p-badge-metrics">
                            <span className="metric-tag time">⏱️ {p.processingTime}s</span>
                            <span className="metric-tag conf">🎯 {p.confidence}%</span>
                          </div>
                        )}
                        <span className="accordion-toggle-arrow">{p.isExpanded ? '▲' : '▼'}</span>
                      </div>
                    </header>

                    {p.isExpanded && (
                      <div className="accordion-body scrollable">
                        <p className="accordion-snippet"><strong>Analysis Strategy:</strong> {p.snippet}</p>
                        <div className="accordion-raw-pre">
                          <Markdown content={p.fullResponse} />
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Final Output Reveal */}
          {currentStep === 'complete' && finalPrompt && (
            <Card title="Optimized Consensus Outcome" subtitle="Merged Prompt generated by AI council.">
              <div className="consensus-results-wrapper animate-fade-in">
                <div className="results-metrics-grid">
                  <div className="metric-box">
                    <span className="m-label">Confidence Score</span>
                    <strong className="m-val">{confidenceScore}%</strong>
                  </div>
                  <div className="metric-box">
                    <span className="m-label">Agreement Score</span>
                    <strong className="m-val">{agreementScore}%</strong>
                  </div>
                  <div className="metric-box">
                    <span className="m-label">Consensus Status</span>
                    <span className="status-tag success">🟢 High Consensus</span>
                  </div>
                </div>

                <div className="consensus-reasoning-bubble">
                  <strong>Consensus reasoning:</strong>
                  <p>{consensusReasoning}</p>
                </div>

                <div className="results-prompt-content scrollable">
                  <Markdown content={finalPrompt} />
                </div>

                <div className="results-actions-row">
                  <Button onClick={handleStartChatSession} variant="primary">
                    💬 Start Chat Session
                  </Button>
                  <Button onClick={handleCopyPrompt} variant="secondary">
                    📋 Copy Prompt
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Empty State */}
          {currentStep === 'idle' && (
            <div className="workspace-empty-state history-empty-state" style={{ minHeight: '260px' }}>
              <div className="empty-state-icon">🏛️</div>
              <h4>Council dashboard is idle</h4>
              <p className="muted text-xs">Configure your topic and click "Start Council Consensus" to witness the multi-agent optimization process.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
export default CouncilPage
