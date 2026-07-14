import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../context/ThemeContext'
import { Button } from '../common/Button'

export const Navbar = () => {
  const { theme, toggleTheme } = useTheme()
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="navbar">
      <div className="brand">AI Thera</div>
      <nav className="nav-links" aria-label="Primary navigation">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        <NavLink to="/settings">Settings</NavLink>
        <NavLink to="/help">Help</NavLink>
      </nav>
      <div className="navbar-actions">
        <Button type="button" variant="secondary" onClick={toggleTheme}>
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </Button>
        {isAuthenticated ? (
          <Button type="button" onClick={handleLogout}>Logout</Button>
        ) : null}
      </div>
    </header>
  )
}
