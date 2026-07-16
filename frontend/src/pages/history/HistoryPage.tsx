import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import { fetchPromptHistory, deletePromptFromHistory, type PromptHistoryItem } from '../../services/api'
import { Markdown } from '../../components/chat/Markdown'

const PAGE_SIZE = 6

export const HistoryPage = () => {
  const navigate = useNavigate()
  const { token } = useAuth()

  // State managers
  const [historyItems, setHistoryItems] = useState<PromptHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStyle, setSelectedStyle] = useState<string>('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all')
  const [showOnlyFavorites, setShowOnlyFavorites] = useState(false)
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest')
  const [currentPage, setCurrentPage] = useState(1)

  // Favorites persistence
  const [favorites, setFavorites] = useState<number[]>(() => {
    const saved = localStorage.getItem('aithera_history_favorites')
    return saved ? JSON.parse(saved) : []
  })

  // Modal triggers
  const [viewItem, setViewItem] = useState<PromptHistoryItem | null>(null)
  const [deleteItem, setDeleteItem] = useState<PromptHistoryItem | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const [sharedId, setSharedId] = useState<number | null>(null)

  // Fetch prompt list on load
  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true)
      try {
        const data = await fetchPromptHistory(token || '')
        setHistoryItems(data)
      } catch (err) {
        console.error('Failed to load prompt history:', err)
      } finally {
        setLoading(false)
      }
    }
    void loadHistory()
  }, [token])

  // Save favorites when changed
  const toggleFavorite = (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    const updated = favorites.includes(id)
      ? favorites.filter(favId => favId !== id)
      : [...favorites, id]
    setFavorites(updated)
    localStorage.setItem('aithera_history_favorites', JSON.stringify(updated))
  }

  // Copy full prompt content
  const handleCopyPrompt = async (item: PromptHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!item.generated_prompt) return
    try {
      await navigator.clipboard.writeText(item.generated_prompt)
      setCopiedId(item.id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy: ', err)
    }
  }

  // Delete Prompt confirmation callback
  const handleDeleteConfirm = async () => {
    if (!deleteItem) return
    try {
      await deletePromptFromHistory(deleteItem.id, token || '')
      setHistoryItems(prev => prev.filter(item => item.id !== deleteItem.id))
      setDeleteItem(null)
      // Reset current page if page is now empty
      const totalFiltered = historyItems.filter(item => item.id !== deleteItem.id).length
      const maxPages = Math.ceil(totalFiltered / PAGE_SIZE)
      if (currentPage > maxPages && maxPages > 0) {
        setCurrentPage(maxPages)
      }
    } catch (err) {
      console.error('Failed to delete prompt:', err)
    }
  }

  // Trigger browser download as a standard TXT file
  const handleDownloadPrompt = (item: PromptHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!item.generated_prompt) return

    const header = `=========================================\n` +
      `AIthera - Educational Prompt File\n` +
      `Generated on: ${new Date(item.created_at).toLocaleString()}\n` +
      `Topic: ${item.topic}\n` +
      `Learning Style: ${item.learning_style}\n` +
      `Difficulty: ${item.difficulty}\n` +
      `=========================================\n\n`
    
    const fileContent = header + item.generated_prompt
    const blob = new Blob([fileContent], { type: 'text/plain;charset=utf-8' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `aithera_prompt_${item.id}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Mock sharing link generator
  const handleSharePrompt = async (item: PromptHistoryItem, e: React.MouseEvent) => {
    e.stopPropagation()
    const mockShareLink = `${window.location.origin}/prompts/${item.id}`
    try {
      await navigator.clipboard.writeText(mockShareLink)
      setSharedId(item.id)
      setTimeout(() => setSharedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy share link:', err)
    }
  }

  // Forward context to continue active chat session
  const handleContinueConversation = (item: PromptHistoryItem) => {
    if (!item.generated_prompt) return
    navigate('/chat', {
      state: {
        initialPrompt: item.generated_prompt,
        topic: item.topic,
        learningStyle: item.learning_style,
        difficulty: item.difficulty
      }
    })
  }

  // Filtering & Sorting
  const filteredItems = historyItems.filter((item) => {
    const matchesSearch =
      item.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.generated_prompt?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
    
    const matchesStyle = selectedStyle === 'all' || item.learning_style === selectedStyle
    const matchesDifficulty = selectedDifficulty === 'all' || item.difficulty === selectedDifficulty
    const matchesFavorite = !showOnlyFavorites || favorites.includes(item.id)

    return matchesSearch && matchesStyle && matchesDifficulty && matchesFavorite
  })

  const sortedItems = [...filteredItems].sort((a, b) => {
    const timeA = new Date(a.created_at).getTime()
    const timeB = new Date(b.created_at).getTime()
    return sortOrder === 'newest' ? timeB - timeA : timeA - timeB
  })

  // Pagination bounds
  const totalItems = sortedItems.length
  const totalPages = Math.ceil(totalItems / PAGE_SIZE)
  const paginatedItems = sortedItems.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  )

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return (
    <div className="history-page-wrapper">
      <header className="history-header">
        <h1>📜 AI Prompt History</h1>
        <p className="muted">Review and manage your generated consensus prompts and study materials.</p>
      </header>

      {/* Search & Filter Toolbar Grid */}
      <section className="history-toolbar-card">
        <div className="toolbar-search-row">
          <label className="field toolbar-search-field">
            <span>🔍 Search Prompts</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setCurrentPage(1) // Reset to page 1
              }}
              placeholder="Search topics or prompt content..."
            />
          </label>
        </div>

        <div className="toolbar-filters-grid">
          <label className="field">
            <span>🧠 Learning Style</span>
            <select
              value={selectedStyle}
              onChange={(e) => {
                setSelectedStyle(e.target.value)
                setCurrentPage(1)
              }}
            >
              <option value="all">All Styles</option>
              <option value="adaptive">Adaptive</option>
              <option value="visual">Visual</option>
              <option value="step_by_step">Step by step</option>
              <option value="conversational">Conversational</option>
              <option value="exam_focused">Exam focused</option>
            </select>
          </label>

          <label className="field">
            <span>🎯 Difficulty</span>
            <select
              value={selectedDifficulty}
              onChange={(e) => {
                setSelectedDifficulty(e.target.value)
                setCurrentPage(1)
              }}
            >
              <option value="all">All Levels</option>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </label>

          <label className="field">
            <span>Sort Order</span>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'newest' | 'oldest')}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </label>

          <div className="favorites-checkbox-cell">
            <label className="checkbox-row favorites-toggle-row">
              <input
                type="checkbox"
                checked={showOnlyFavorites}
                onChange={(e) => {
                  setShowOnlyFavorites(e.target.checked)
                  setCurrentPage(1)
                }}
              />
              <span>⭐ Show Favorites Only</span>
            </label>
          </div>
        </div>
      </section>

      {/* Main Grid View */}
      <section className="history-content-stream">
        {loading ? (
          // Loading skeletons
          <div className="history-cards-grid">
            {[1, 2, 3, 4].map(idx => (
              <div key={idx} className="card skeleton-card">
                <div className="skeleton-title" />
                <div className="skeleton-badges" />
                <div className="skeleton-text" />
                <div className="skeleton-actions" />
              </div>
            ))}
          </div>
        ) : paginatedItems.length > 0 ? (
          <div className="history-cards-grid">
            {paginatedItems.map((item) => {
              const isFav = favorites.includes(item.id)
              const hasPrompt = !!item.generated_prompt
              
              return (
                <div key={item.id} className="card history-item-card animate-fade-in">
                  <header className="history-card-header">
                    <h3 className="history-card-topic" title={item.topic}>
                      {item.topic}
                    </h3>
                    <button
                      type="button"
                      className={`favorite-star-btn ${isFav ? 'active' : ''}`}
                      onClick={(e) => toggleFavorite(item.id, e)}
                      title={isFav ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      ★
                    </button>
                  </header>

                  <div className="history-card-badges">
                    <span className="prompt-badge style-badge">{item.learning_style}</span>
                    <span className="prompt-badge diff-badge">{item.difficulty}</span>
                    <span className={`status-tag ${hasPrompt ? 'success' : 'pending'}`}>
                      {hasPrompt ? '● Completed' : '○ Empty'}
                    </span>
                  </div>

                  <p className="history-card-date">
                    📅 {new Date(item.created_at).toLocaleString(undefined, {
                      dateStyle: 'medium',
                      timeStyle: 'short'
                    })}
                  </p>

                  <div className="history-card-snippet">
                    {item.generated_prompt
                      ? item.generated_prompt.substring(0, 120).replace(/[#*`]/g, '') + '...'
                      : 'No generated prompt text found in database.'}
                  </div>

                  <footer className="history-card-actions">
                    <div className="left-actions">
                      <button
                        type="button"
                        className="history-action-btn view"
                        onClick={() => setViewItem(item)}
                        title="View details"
                      >
                        👁️ View
                      </button>
                      {hasPrompt && (
                        <button
                          type="button"
                          className="history-action-btn chat"
                          onClick={() => handleContinueConversation(item)}
                          title="Continue to chat workspace"
                        >
                          💬 Chat
                        </button>
                      )}
                    </div>

                    <div className="right-actions-tray">
                      {hasPrompt && (
                        <>
                          <button
                            type="button"
                            className="history-tray-btn"
                            onClick={(e) => handleCopyPrompt(item, e)}
                            title="Copy prompt text"
                          >
                            {copiedId === item.id ? '✅' : '📋'}
                          </button>
                          <button
                            type="button"
                            className="history-tray-btn"
                            onClick={(e) => handleDownloadPrompt(item, e)}
                            title="Download as text file"
                          >
                            📥
                          </button>
                          <button
                            type="button"
                            className="history-tray-btn"
                            onClick={(e) => handleSharePrompt(item, e)}
                            title="Copy share link"
                          >
                            {sharedId === item.id ? '✅' : '📤'}
                          </button>
                        </>
                      )}
                      <button
                        type="button"
                        className="history-tray-btn delete"
                        onClick={() => setDeleteItem(item)}
                        title="Delete prompt"
                      >
                        🗑️
                      </button>
                    </div>
                  </footer>
                </div>
              )
            })}
          </div>
        ) : (
          /* Empty state */
          <div className="workspace-empty-state history-empty-state">
            <div className="empty-state-icon">📜</div>
            <h4>No prompt records found</h4>
            <p className="muted text-xs">
              Try adjusting your search query, clearing your filters, or generating a new prompt in the Workspace page.
            </p>
            <Button onClick={() => navigate('/workspace')} variant="primary">
              ✨ Go to AI Workspace
            </Button>
          </div>
        )}
      </section>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <nav className="history-pagination" aria-label="Pagination">
          <button
            type="button"
            className="pagination-arrow-btn"
            disabled={currentPage === 1}
            onClick={() => handlePageChange(currentPage - 1)}
          >
            ◀ Prev
          </button>
          
          <div className="pagination-pills">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((pNum) => (
              <button
                key={pNum}
                type="button"
                className={`pagination-pill ${currentPage === pNum ? 'active' : ''}`}
                onClick={() => handlePageChange(pNum)}
              >
                {pNum}
              </button>
            ))}
          </div>

          <button
            type="button"
            className="pagination-arrow-btn"
            disabled={currentPage === totalPages}
            onClick={() => handlePageChange(currentPage + 1)}
          >
            Next ▶
          </button>
        </nav>
      )}

      {/* View Prompt Modal Overlay */}
      {viewItem && (
        <div className="modal-overlay" onClick={() => setViewItem(null)}>
          <div className="modal-card animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <header className="modal-header">
              <div>
                <h2>Expanded prompt preview</h2>
                <p className="muted text-xs">Topic: **{viewItem.topic}**</p>
              </div>
              <button
                type="button"
                className="modal-close-x"
                onClick={() => setViewItem(null)}
              >
                ×
              </button>
            </header>

            <div className="modal-body scrollable">
              {viewItem.generated_prompt ? (
                <Markdown content={viewItem.generated_prompt} />
              ) : (
                <p className="muted italic">No generated prompt context available for this request.</p>
              )}
            </div>

            <footer className="modal-footer">
              {viewItem.generated_prompt && (
                <Button
                  onClick={() => handleContinueConversation(viewItem)}
                  variant="primary"
                >
                  💬 Continue in Chat
                </Button>
              )}
              <Button onClick={() => setViewItem(null)} variant="secondary">
                Close
              </Button>
            </footer>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal Overlay */}
      {deleteItem && (
        <div className="modal-overlay" onClick={() => setDeleteItem(null)}>
          <div className="modal-card confirm-modal animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <header className="modal-header">
              <h2>Confirm Deletion</h2>
              <button
                type="button"
                className="modal-close-x"
                onClick={() => setDeleteItem(null)}
              >
                ×
              </button>
            </header>

            <div className="modal-body">
              <p>Are you sure you want to delete the prompt request for **"{deleteItem.topic}"**?</p>
              <p className="muted text-xs">This action is permanent and cannot be undone.</p>
            </div>

            <footer className="modal-footer">
              <Button onClick={handleDeleteConfirm} variant="primary" style={{ backgroundColor: '#dc2626' }}>
                🗑️ Confirm Delete
              </Button>
              <Button onClick={() => setDeleteItem(null)} variant="secondary">
                Cancel
              </Button>
            </footer>
          </div>
        </div>
      )}
    </div>
  )
}
export default HistoryPage
