import { useNavigate } from 'react-router-dom'
import { Card } from '../common/Card'

type QuickAction = {
  label: string
  path: string
  description: string
}

const actions: QuickAction[] = [
  { label: 'Generate Prompt', path: '/dashboard', description: 'Create your next challenge' },
  { label: 'Continue Learning', path: '/dashboard', description: 'Pick up where you left off' },
  { label: 'View History', path: '/profile', description: 'Review saved progress' },
  { label: 'Profile', path: '/profile', description: 'Manage your account' },
  { label: 'Settings', path: '/settings', description: 'Tune your experience' },
]

export const QuickActions = () => {
  const navigate = useNavigate()

  return (
    <Card title="Quick actions">
      <div className="quick-actions-grid">
        {actions.map((action) => (
          <button key={action.label} type="button" className="quick-action-card" onClick={() => navigate(action.path)}>
            <strong>{action.label}</strong>
            <span>{action.description}</span>
          </button>
        ))}
      </div>
    </Card>
  )
}
