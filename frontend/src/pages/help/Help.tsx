import { useState } from 'react'
import { Card } from '../../components/common/Card'
import { Button } from '../../components/common/Button'
import { useToast } from '../../context/ToastContext'

type TabId = 'faq' | 'about' | 'contact' | 'legal'

type FAQItem = {
  question: string
  answer: string
}

const FAQS: FAQItem[] = [
  {
    question: 'How does the AI Council generation work?',
    answer: 'AIthera uses a multi-agent consensus model. When you input a topic, GPT, Claude, Gemini, and DeepSeek draft independent versions. The Consensus Engine analyzes contributions, scores structural alignment, and merges them into a single, optimized prompt matching your learning style.',
  },
  {
    question: 'What are the available learning styles?',
    answer: 'We support: Visual (includes ASCII drawings and flowcharts), Step-by-Step (structured incremental blocks), Conversational (Socratic dialogue and analogies), Adaptive (dynamic level shifts), and Exam-Focused (problem-solving checklists).',
  },
  {
    question: 'How do I use Speech-to-Text dictation?',
    answer: 'Click the microphone icon inside the topic or chat inputs. If your browser supports WebSpeech, it will dictate live. If unsupported, the simulator will showcase sample prompt typing so you can test it.',
  },
  {
    question: 'Can I upload files or images?',
    answer: 'Yes! Go to the "Image Upload" page to drop up to 3 files (max 5MB each). You can run OCR vision simulation to extract the text and forward it directly to the Workspace or Chat pages.',
  },
]

export const HelpPage = () => {
  const { showToast, dismissToast } = useToast()
  const [activeTab, setActiveTab] = useState<TabId>('faq')
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)

  // Feedback Form State
  const [feedback, setFeedback] = useState({
    name: '',
    email: '',
    subject: 'General Feedback',
    message: '',
  })
  const [submitting, setSubmitting] = useState(false)

  const handleFaqToggle = (idx: number) => {
    setExpandedFaq(prev => (prev === idx ? null : idx))
  }

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!feedback.name || !feedback.email || !feedback.message) {
      showToast('Please fill out all required form fields.', 'error')
      return
    }

    setSubmitting(true)
    const toastId = showToast('Submitting feedback...', 'loading', 0)

    // Simulate network latency
    await new Promise(resolve => setTimeout(resolve, 1500))

    dismissToast(toastId)
    showToast('Feedback submitted successfully! Thank you.', 'success')
    setSubmitting(false)
    setFeedback({
      name: '',
      email: '',
      subject: 'General Feedback',
      message: '',
    })
  }

  return (
    <div className="help-page-container animate-fade-in">
      <header className="help-page-header">
        <h1>❓ Support & Help Center</h1>
        <p className="muted">Find onboarding guides, read our FAQ, or contact support.</p>
      </header>

      <div className="help-dashboard-grid">
        {/* Navigation Tabs List */}
        <aside className="help-tabs-sidebar">
          <button
            type="button"
            className={`help-tab-btn ${activeTab === 'faq' ? 'active' : ''}`}
            onClick={() => setActiveTab('faq')}
          >
            📋 FAQ & Guides
          </button>
          <button
            type="button"
            className={`help-tab-btn ${activeTab === 'about' ? 'active' : ''}`}
            onClick={() => setActiveTab('about')}
          >
            🏛️ About AIthera
          </button>
          <button
            type="button"
            className={`help-tab-btn ${activeTab === 'contact' ? 'active' : ''}`}
            onClick={() => setActiveTab('contact')}
          >
            ✉️ Contact & Feedback
          </button>
          <button
            type="button"
            className={`help-tab-btn ${activeTab === 'legal' ? 'active' : ''}`}
            onClick={() => setActiveTab('legal')}
          >
            ⚖️ Legal & Policies
          </button>
        </aside>

        {/* Tab Viewport Content Panels */}
        <main className="help-tab-viewport">
          {activeTab === 'faq' && (
            <Card title="Frequently Asked Questions" subtitle="Quick solutions to general workflow questions.">
              <div className="faq-accordions-group">
                {FAQS.map((faq, idx) => {
                  const isOpen = expandedFaq === idx
                  return (
                    <div key={idx} className="faq-accordion-item">
                      <header
                        className="faq-header"
                        onClick={() => handleFaqToggle(idx)}
                        role="button"
                        aria-expanded={isOpen}
                        tabIndex={0}
                        onKeyDown={(e) => e.key === 'Enter' && handleFaqToggle(idx)}
                      >
                        <strong>{faq.question}</strong>
                        <span className="faq-arrow">{isOpen ? '▲' : '▼'}</span>
                      </header>
                      {isOpen && (
                        <div className="faq-body">
                          <p>{faq.answer}</p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </Card>
          )}

          {activeTab === 'about' && (
            <Card title="About AIthera" subtitle="The Prompt Playground for Every Learning Style.">
              <div className="about-tech-content">
                <p>
                  <strong>AIthera</strong> is an educational prompt-engineering workspace built on the premise that
                  one size does not fit all. By leveraging a multi-agent AI Council (featuring model configurations
                  from OpenAI, Anthropic, Google, and DeepSeek), we align complex educational tasks with the specific
                  cognitive styles of the learner.
                </p>

                <h4>Our Technology Stack</h4>
                <ul className="bullet-list-style">
                  <li><strong>Frontend:</strong> React 19, TypeScript, Vite, Vanilla CSS design tokens.</li>
                  <li><strong>Backend:</strong> FastAPI, SQLAlchemy database layer.</li>
                  <li><strong>AI Engine:</strong> Speech Recognition APIs, Speech Synthesis, OCR and Vision simulators, Multi-agent LLM wrappers.</li>
                </ul>

                <h4>Design Aesthetic</h4>
                <p>
                  Built with a <strong>Kawaii Professional</strong> aesthetic, AIthera pairs approachable geometry
                  and glassmorphism with high-contrast inputs and typing animations. The goal is to make learning
                  visually engaging and satisfyingly responsive.
                </p>
              </div>
            </Card>
          )}

          {activeTab === 'contact' && (
            <Card title="Contact Support & Feedback" subtitle="Submit feedback or report an interface bug.">
              <form className="feedback-form" onSubmit={handleFeedbackSubmit}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <label className="field">
                    <span>Name <span style={{ color: '#dc2626' }}>*</span></span>
                    <input
                      type="text"
                      required
                      value={feedback.name}
                      onChange={(e) => setFeedback({ ...feedback, name: e.target.value })}
                      placeholder="Learner Name"
                      disabled={submitting}
                    />
                  </label>

                  <label className="field">
                    <span>Email Address <span style={{ color: '#dc2626' }}>*</span></span>
                    <input
                      type="email"
                      required
                      value={feedback.email}
                      onChange={(e) => setFeedback({ ...feedback, email: e.target.value })}
                      placeholder="learner@aithera.edu"
                      disabled={submitting}
                    />
                  </label>
                </div>

                <label className="field">
                  <span>Subject</span>
                  <select
                    value={feedback.subject}
                    onChange={(e) => setFeedback({ ...feedback, subject: e.target.value })}
                    disabled={submitting}
                  >
                    <option value="General Feedback">General Feedback</option>
                    <option value="Bug Report">Interface Bug Report</option>
                    <option value="Feature Request">Feature Request</option>
                    <option value="Model Request">AI Provider Request</option>
                  </select>
                </label>

                <label className="field">
                  <span>Feedback Message <span style={{ color: '#dc2626' }}>*</span></span>
                  <textarea
                    rows={4}
                    required
                    value={feedback.message}
                    onChange={(e) => setFeedback({ ...feedback, message: e.target.value })}
                    placeholder="Describe your request or share your experience..."
                    disabled={submitting}
                  />
                </label>

                <Button type="submit" variant="primary" disabled={submitting}>
                  {submitting ? 'Submitting...' : '✉️ Submit Ticket'}
                </Button>
              </form>
            </Card>
          )}

          {activeTab === 'legal' && (
            <Card title="Legal & Policies" subtitle="Terms of service and user privacy statements.">
              <div className="legal-policy-panels">
                <section className="legal-section-block">
                  <h4>1. Terms & Conditions</h4>
                  <p className="muted text-xs text-justify">
                    By using AIthera, you agree to access LLM services in a simulated and educational manner.
                    All prompts generated are public recommendations and do not represent professional legal or financial advice.
                  </p>
                </section>
                
                <section className="legal-section-block" style={{ marginTop: '1rem' }}>
                  <h4>2. Privacy Policy</h4>
                  <p className="muted text-xs text-justify">
                    We value your data privacy. Voice transcriptions and image snapshots are processed locally on your client machine
                    using standard browser Web Speech and Media Device APIs. Prompt request histories are stored in the local SQLite/SQLAlchemy
                    database and are protected under JWT token validation.
                  </p>
                </section>
              </div>
            </Card>
          )}
        </main>
      </div>
    </div>
  )
}
export default HelpPage
