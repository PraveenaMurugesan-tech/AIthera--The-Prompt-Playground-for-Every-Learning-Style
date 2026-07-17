import { useAuth } from '../../context/AuthContext'
import { Card } from '../common/Card'

type ProfileOverviewCardProps = {
  learningStyle?: string
}

export const ProfileOverviewCard = ({ learningStyle = 'Adaptive' }: ProfileOverviewCardProps) => {
  const { currentUser } = useAuth()

  return (
    <Card title="Profile overview">
      <div className="profile-overview">
        <div className="avatar-placeholder">{(currentUser?.name || currentUser?.email || 'U').charAt(0).toUpperCase()}</div>
        <div className="profile-overview-meta">
          <h3>{currentUser?.name || 'Learner'}</h3>
          <p>{currentUser?.email || 'No email available'}</p>
          <p className="muted">Preferred learning style: {learningStyle}</p>
        </div>
      </div>
    </Card>
  )
}
