import { useState, useRef, useEffect } from 'react'
import './PromptInputBar.css'

export const PromptInputBar = () => {
  const [query, setQuery] = useState('')
  const [showOptions, setShowOptions] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowOptions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="prompt-input-container">
      {showOptions && (
        <div className="prompt-options-menu" ref={menuRef}>
          <button className="option-item">
            <span className="option-icon">📎</span>
            <div className="option-text">
              <strong>Add photos & files</strong>
              <span>Upload from computer</span>
            </div>
          </button>
          <button className="option-item">
            <span className="option-icon">🎨</span>
            <div className="option-text">
              <strong>Create image</strong>
              <span>Visualize anything</span>
            </div>
          </button>
          <button className="option-item">
            <span className="option-icon">🔍</span>
            <div className="option-text">
              <strong>Deep research</strong>
              <span>Get a detailed report</span>
            </div>
          </button>
          <div className="option-search">
            <input type="text" placeholder="Type to search plugins, files, folders & skills" />
          </div>
        </div>
      )}
      
      <div className="prompt-input-bar">
        <button 
          className="add-btn" 
          aria-label="Add attachment"
          onClick={() => setShowOptions(!showOptions)}
        >
          ＋
        </button>
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything" 
          className="prompt-input"
        />
        <div className="prompt-actions">
          <button className="mic-btn" aria-label="Voice input">
            🎙️
          </button>
          <button className="send-btn" aria-label="Send">
            <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
