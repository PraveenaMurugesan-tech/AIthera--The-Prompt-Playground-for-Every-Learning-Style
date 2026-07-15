import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import { Button } from '../common/Button'

export const Navbar = () => {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, logout, currentUser } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="navbar">
      <div className="brand-wrap">
        <div className="brand-mark">A</div>
        <div>
          <div className="brand">AIthera</div>
          <div className="brand-subtitle">Learning workspace</div>
        </div>
      </div>

      <div className="navbar-actions">
        <button type="button" className="icon-button" aria-label="Toggle theme" onClick={toggleTheme}>
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        <button type="button" className="icon-button" aria-label="Notifications">
          🔔
        </button>
        <div className="avatar-pill" aria-label="Current user">
          <span className="avatar-dot">{(currentUser?.name || currentUser?.email || 'U').charAt(0).toUpperCase()}</span>
          <span className="avatar-label">{currentUser?.name || 'Learner'}</span>
        </div>
        {isAuthenticated ? (
          <Button type="button" variant="secondary" onClick={handleLogout}>Logout</Button>
        ) : null}
      </div>
    </header>
  )
}
