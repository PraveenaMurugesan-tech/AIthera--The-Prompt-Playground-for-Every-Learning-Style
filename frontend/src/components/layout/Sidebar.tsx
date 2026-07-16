import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
  { to: '/workspace', label: 'AI Workspace', icon: '✨' },
  { to: '/history', label: 'Prompt History', icon: '📜' },
  { to: '/chat', label: 'Chat', icon: '💬' },
  { to: '/image-upload', label: 'Image Upload', icon: '🖼' },
  { to: '/voice', label: 'Voice', icon: '🎤' },
  { to: '/profile', label: 'Profile', icon: '👤' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
  { to: '/help', label: 'Help', icon: '❓' },
]

export const Sidebar = () => {
  return (
    <aside className="sidebar" aria-label="Sidebar navigation">
      <div className="sidebar-section">
        <p className="sidebar-heading">Main</p>
        <nav className="sidebar-nav">
          {links.map((link) => (
            <NavLink key={link.to + link.label} to={link.to} className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
              <span className="sidebar-icon">{link.icon}</span>
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}
