import { NavLink } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { Button } from '../common/Button'

export const Navbar = () => {
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="navbar">
      <div className="brand">AI Thera</div>
      <nav className="nav-links" aria-label="Primary navigation">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        <NavLink to="/settings">Settings</NavLink>
        <NavLink to="/help">Help</NavLink>
      </nav>
      <Button type="button" variant="secondary" onClick={toggleTheme}>
        {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
      </Button>
    </header>
  )
}
