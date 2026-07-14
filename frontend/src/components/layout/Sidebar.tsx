import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/profile', label: 'Profile' },
  { to: '/settings', label: 'Settings' },
  { to: '/help', label: 'Help' },
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
