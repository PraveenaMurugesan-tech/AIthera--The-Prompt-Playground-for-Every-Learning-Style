import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Button } from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import { sendChatMessage, type Conversation, type Message, type LearningStyle, type Difficulty } from '../../services/chatApi'
import { Markdown } from '../../components/chat/Markdown'

const SUGGESTIONS = [
  'Explain this topic in simple terms with an analogy.',
  'Give me a step-by-step practical coding challenge.',
  'Test my understanding with a 3-question quiz.',
  'What are the key design patterns related to this?'
]

const DEFAULT_CONVERSATIONS: Conversation[] = [
  {
    id: 'welcome_chat',
    title: '👋 Welcome to AIthera Chat',
    learningStyle: 'conversational',
    difficulty: 'intermediate',
    messages: [
      {
        id: 'msg_welcome',
        role: 'assistant',
        content: `### Hello, Learner! 🌟

Welcome to **AIthera AI Chat Experience**. I am your personal AI learning coach, simulated by the AI Council.

I am here to help you study topics, write code, run exercises, or prep for interviews. You can customize my behavior to match your unique learning style:
- 🎨 **Visual**: Focuses on diagrams, tables, and map structures.
- 🪜 **Step by step**: Provides code blocks, guides, and numbered phases.
- 💬 **Conversational**: Chat-driven explanations and everyday analogies.
- 📝 **Exam focused**: Practical tests, trap tips, and multiple-choice questions.
- 🪐 **Adaptive**: Matches your topic's speed and changes based on input.

Use the dropdowns in the header to change your learning style and difficulty settings at any point! Start by typing a topic in the input below, or choose one of the quick suggestions.`,
        timestamp: Date.now(),
        provider: 'AI Council'
      }
    ],
    createdAt: Date.now()
  }
]

export const ChatPage = () => {
  const { token, currentUser } = useAuth()
  const location = useLocation()

  // State
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string>('welcome_chat')
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  
  // Refs
  const messageEndRef = useRef<HTMLDivElement | null>(null)

  // Load chats from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('aithera_chats')
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as Conversation[]
        if (parsed.length > 0) {
          setConversations(parsed)
          setActiveId(parsed[0].id)
        } else {
          setConversations(DEFAULT_CONVERSATIONS)
          setActiveId('welcome_chat')
        }
      } catch {
        setConversations(DEFAULT_CONVERSATIONS)
        setActiveId('welcome_chat')
      }
    } else {
      setConversations(DEFAULT_CONVERSATIONS)
      setActiveId('welcome_chat')
    }
  }, [])

  // Auto-save conversations when they change
  const saveConversations = (updated: Conversation[]) => {
    setConversations(updated)
    localStorage.setItem('aithera_chats', JSON.stringify(updated))
  }

  // Handle Workspace Navigation State integration
  useEffect(() => {
    const navState = location.state as {
      initialPrompt?: string
      topic?: string
      learningStyle?: LearningStyle
      difficulty?: Difficulty
    } | null

    if (navState?.initialPrompt && navState?.topic) {
      const topic = navState.topic
      const newId = 'conv_' + Date.now()
      const newConv: Conversation = {
        id: newId,
        title: `Workspace: ${topic.length > 20 ? topic.substring(0, 20) + '...' : topic}`,
        learningStyle: navState.learningStyle || 'adaptive',
        difficulty: navState.difficulty || 'intermediate',
        messages: [
          {
            id: 'msg_usr_' + Date.now(),
            role: 'user',
            content: `I'd like to learn about "${topic}" in ${navState.learningStyle || 'adaptive'} style. Here is my generated starting prompt.`,
            timestamp: Date.now() - 1000
          },
          {
            id: 'msg_asst_' + Date.now(),
            role: 'assistant',
            content: navState.initialPrompt,
            timestamp: Date.now(),
            learningStyle: navState.learningStyle || 'adaptive',
            difficulty: navState.difficulty || 'intermediate',
            provider: 'AI Council'
          }
        ],
        createdAt: Date.now()
      }

      const updated = [newConv, ...conversations.filter(c => c.id !== 'welcome_chat')]
      saveConversations(updated)
      setActiveId(newId)

      // Clean the browser history state so refresh won't duplicate this thread
      window.history.replaceState({}, document.title)
    }
  }, [location.state, conversations])

  // Get active conversation details
  const activeChat = conversations.find((c) => c.id === activeId) || DEFAULT_CONVERSATIONS[0]

  // Auto scroll to latest message
  const scrollToBottom = () => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [activeChat.messages, isTyping])

  // Create new conversation
  const handleCreateNewChat = () => {
    const newId = 'conv_' + Date.now()
    const newChat: Conversation = {
      id: newId,
      title: 'New Chat session',
      learningStyle: 'adaptive',
      difficulty: 'intermediate',
      messages: [
        {
          id: 'msg_welcome_' + Date.now(),
          role: 'assistant',
          content: 'Hello! I am ready for our next learning topic. What would you like to explore today?',
          timestamp: Date.now(),
          provider: 'AI Council'
        }
      ],
      createdAt: Date.now()
    }
    
    const updated = [newChat, ...conversations]
    saveConversations(updated)
    setActiveId(newId)
    setErrorMessage(null)
  }

  // Delete conversation
  const handleDeleteChat = (idToDelete: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const updated = conversations.filter(c => c.id !== idToDelete)
    saveConversations(updated)
    
    if (activeId === idToDelete) {
      if (updated.length > 0) {
        setActiveId(updated[0].id)
      } else {
        setConversations(DEFAULT_CONVERSATIONS)
        setActiveId('welcome_chat')
      }
    }
  }

  // Update configurations mid-chat
  const handleUpdateSettings = (key: 'learningStyle' | 'difficulty', value: string) => {
    const updated = conversations.map(c => {
      if (c.id === activeId) {
        return { ...c, [key]: value }
      }
      return c
    })
    saveConversations(updated)
  }

  // Send message
  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || isTyping) return

    setErrorMessage(null)
    const userMsgText = textToSend.trim()
    setInputText('')

    // 1. Append user message
    const userMessage: Message = {
      id: 'msg_u_' + Date.now(),
      role: 'user',
      content: userMsgText,
      timestamp: Date.now()
    }

    let updatedMessages = [...activeChat.messages, userMessage]
    
    // Auto-update conversation title if it was default
    let chatTitle = activeChat.title
    if (chatTitle === 'New Chat session' || chatTitle === '👋 Welcome to AIthera Chat') {
      chatTitle = userMsgText.length > 25 ? userMsgText.substring(0, 25) + '...' : userMsgText
    }

    const updatedChat: Conversation = {
      ...activeChat,
      title: chatTitle,
      messages: updatedMessages
    }

    const updatedList = conversations.map(c => c.id === activeId ? updatedChat : c)
    saveConversations(updatedList)
    setIsTyping(true)

    try {
      // 2. Fetch AI response
      const aiResponse = await sendChatMessage(updatedChat, userMsgText, token || undefined)
      
      const finalChat = {
        ...updatedChat,
        messages: [...updatedMessages, aiResponse]
      }
      
      const finalList = conversations.map(c => c.id === activeId ? finalChat : c)
      saveConversations(finalList)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Unable to retrieve response from AI Council.')
    } finally {
      setIsTyping(false)
    }
  }

  // Copy full response text
  const handleCopyResponse = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (err) {
      console.error('Failed to copy response: ', err)
    }
  }

  // Regenerate Response
  const handleRegenerateResponse = async () => {
    if (isTyping) return

    // Find the last user message in the thread
    const msgs = [...activeChat.messages]
    let lastUserIndex = -1
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].role === 'user') {
        lastUserIndex = i
        break
      }
    }

    if (lastUserIndex === -1) return

    setErrorMessage(null)
    setIsTyping(true)

    const userMessage = msgs[lastUserIndex]
    // Strip everything after this user message
    const trimmedMessages = msgs.slice(0, lastUserIndex + 1)
    
    const updatedChat: Conversation = {
      ...activeChat,
      messages: trimmedMessages
    }

    const updatedList = conversations.map(c => c.id === activeId ? updatedChat : c)
    saveConversations(updatedList)

    try {
      const aiResponse = await sendChatMessage(updatedChat, userMessage.content, token || undefined)
      const finalChat = {
        ...updatedChat,
        messages: [...trimmedMessages, aiResponse]
      }
      const finalList = conversations.map(c => c.id === activeId ? finalChat : c)
      saveConversations(finalList)
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to regenerate response.')
    } finally {
      setIsTyping(false)
    }
  }

  // Clear current conversation
  const handleClearConversation = () => {
    const updated = conversations.map(c => {
      if (c.id === activeId) {
        return {
          ...c,
          messages: [
            {
              id: 'msg_clear_' + Date.now(),
              role: 'assistant' as const,
              content: 'Conversation history cleared. Ready for your questions!',
              timestamp: Date.now(),
              provider: 'AI Council'
            }
          ]
        }
      }
      return c
    })
    saveConversations(updated)
    setErrorMessage(null)
  }

  // Keypress handler for input
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(inputText)
    }
  }

  return (
    <div className="chat-layout-wrapper">
      {/* Sidebar Panel */}
      <aside className="chat-sidebar" aria-label="Chat sessions">
        <div className="chat-sidebar-header">
          <Button onClick={handleCreateNewChat} variant="primary">
            ➕ New Chat
          </Button>
        </div>
        
        <nav className="chat-thread-list">
          {conversations.map((c) => {
            const isActive = c.id === activeId
            return (
              <button
                key={c.id}
                type="button"
                className={`chat-thread-item ${isActive ? 'active' : ''}`}
                onClick={() => {
                  setActiveId(c.id)
                  setErrorMessage(null)
                }}
              >
                <div className="thread-content-left">
                  <span className="thread-icon">💬</span>
                  <span className="thread-title">{c.title}</span>
                </div>
                {c.id !== 'welcome_chat' && (
                  <button
                    type="button"
                    className="thread-delete-btn"
                    onClick={(e) => handleDeleteChat(c.id, e)}
                    aria-label="Delete conversation"
                  >
                    🗑️
                  </button>
                )}
              </button>
            )
          })}
        </nav>
        
        <div className="chat-sidebar-footer">
          <p className="muted text-xs">Logged in as {currentUser?.name || 'Learner'}</p>
        </div>
      </aside>

      {/* Main Chat Workspace */}
      <section className="chat-workspace">
        {/* Header - Settings controls */}
        <header className="chat-workspace-header">
          <div className="chat-meta-info">
            <h2>{activeChat.title}</h2>
            <div className="chat-settings-pills">
              <label className="chat-pill-select">
                <span>🧠 Style:</span>
                <select
                  value={activeChat.learningStyle}
                  onChange={(e) => handleUpdateSettings('learningStyle', e.target.value)}
                >
                  <option value="adaptive">Adaptive</option>
                  <option value="visual">Visual</option>
                  <option value="step_by_step">Step by step</option>
                  <option value="conversational">Conversational</option>
                  <option value="exam_focused">Exam focused</option>
                </select>
              </label>

              <label className="chat-pill-select">
                <span>🎯 Difficulty:</span>
                <select
                  value={activeChat.difficulty}
                  onChange={(e) => handleUpdateSettings('difficulty', e.target.value)}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </label>
            </div>
          </div>

          <div className="chat-header-actions">
            <Button onClick={handleClearConversation} variant="secondary">
              🧹 Clear Chat
            </Button>
          </div>
        </header>

        {/* Message bubble stream */}
        <div className="chat-messages-container">
          {activeChat.messages.map((message) => {
            const isUser = message.role === 'user'
            return (
              <div
                key={message.id}
                className={`chat-message-row ${isUser ? 'user-row' : 'ai-row'}`}
              >
                {!isUser && (
                  <div className="chat-avatar-container">
                    <div className="chat-avatar-orb">
                      <span>✦</span>
                    </div>
                  </div>
                )}

                <div className={`chat-bubble ${isUser ? 'user-bubble' : 'ai-bubble'}`}>
                  {!isUser && (
                    <div className="chat-bubble-meta">
                      <strong>AI Council Simulator</strong>
                      {message.provider && (
                        <span className="chat-provider-badge">{message.provider}</span>
                      )}
                    </div>
                  )}
                  
                  <div className="chat-bubble-text">
                    {isUser ? (
                      <p>{message.content}</p>
                    ) : (
                      <Markdown content={message.content} />
                    )}
                  </div>

                  {!isUser && (
                    <div className="chat-bubble-actions">
                      <button
                        type="button"
                        className="bubble-action-btn"
                        onClick={() => handleCopyResponse(message.content)}
                        title="Copy response"
                      >
                        📋 Copy
                      </button>
                      {activeChat.messages[activeChat.messages.length - 1].id === message.id && (
                        <button
                          type="button"
                          className="bubble-action-btn"
                          onClick={handleRegenerateResponse}
                          title="Regenerate response"
                        >
                          🔄 Regenerate
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )
          })}

          {isTyping && (
            <div className="chat-message-row ai-row">
              <div className="chat-avatar-container">
                <div className="chat-avatar-orb pulse">
                  <span>✦</span>
                </div>
              </div>
              <div className="chat-bubble ai-bubble typing-bubble">
                <div className="typing-indicator">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="status-banner error chat-error-banner">
              ⚠️ {errorMessage}
            </div>
          )}

          <div ref={messageEndRef} />
        </div>

        {/* Suggestion Chips */}
        {activeChat.messages.length <= 1 && (
          <div className="chat-suggestions-tray">
            <p className="muted text-xs">Quick suggestions to start:</p>
            <div className="chat-suggestions-grid">
              {SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleSendMessage(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input box form */}
        <footer className="chat-input-wrapper">
          <form
            className="chat-input-form"
            onSubmit={(e) => {
              e.preventDefault()
              handleSendMessage(inputText)
            }}
          >
            <div className="chat-textarea-shell">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask your AI learning coach a question... (Enter to send, Shift+Enter for new line)"
                rows={1}
                disabled={isTyping}
              />
              <button
                type="submit"
                className="chat-send-btn"
                disabled={!inputText.trim() || isTyping}
                aria-label="Send message"
              >
                ⚡
              </button>
            </div>
            <div className="chat-input-footer">
              <p className="muted text-xs">
                Simulating with **AI Council**. Active style: **{activeChat.learningStyle}** • Difficulty: **{activeChat.difficulty}**.
              </p>
            </div>
          </form>
        </footer>
      </section>
    </div>
  )
}
