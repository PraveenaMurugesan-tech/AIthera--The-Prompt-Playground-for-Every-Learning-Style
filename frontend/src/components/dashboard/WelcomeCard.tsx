import { useAuth } from '../../context/AuthContext'
import { Card } from '../common/Card'

type WelcomeCardProps = {
  title?: string
}

export const WelcomeCard = ({ title = 'Welcome back' }: WelcomeCardProps) => {
  const { currentUser } = useAuth()

  return (
    <Card title={title}>
      <div className="welcome-card-content">
        <div>
          <p className="muted">{currentUser?.name || currentUser?.email || 'Learner'} — your next breakthrough is waiting.</p>
          <p className="welcome-message">Keep building confidence with guided prompts, thoughtful explanations, and focused practice.</p>
        </div>
        <div className="welcome-badge">Ready to learn</div>
      </div>
    </Card>
  )
}
