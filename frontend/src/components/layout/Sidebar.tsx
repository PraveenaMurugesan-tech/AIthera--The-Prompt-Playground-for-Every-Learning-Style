import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/prompt', label: 'Generate Prompt' },
  { to: '/chat', label: 'AI Chat' },
  { to: '/council', label: 'AI Council' },
  { to: '/history', label: 'History' },
  { to: '/voice', label: 'Voice Learning' },
  { to: '/upload', label: 'Image Upload' },
  { to: '/recommendations', label: 'AI Recommendations' },
]

export const Sidebar = () => {
  return (
    <aside className="sidebar">
      <h2>Explore</h2>
      <nav className="sidebar-nav">
        {links.map((link) => (
          <NavLink key={link.to} to={link.to}>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
