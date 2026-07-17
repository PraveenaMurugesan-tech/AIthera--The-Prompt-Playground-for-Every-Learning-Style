import { useAuth } from '../../context/AuthContext'
import { Card } from '../common/Card'

type ProfileSummaryCardProps = {
  learningStyle?: string
  memberSince?: string
}

export const ProfileSummaryCard = ({ learningStyle = 'Adaptive', memberSince = 'Joined recently' }: ProfileSummaryCardProps) => {
  const { currentUser } = useAuth()

  return (
    <Card title="Profile summary">
      <div className="profile-summary-grid">
        <div>
          <p className="summary-label">Name</p>
          <p>{currentUser?.name || 'Not provided'}</p>
        </div>
        <div>
          <p className="summary-label">Email</p>
          <p>{currentUser?.email || 'Unavailable'}</p>
        </div>
        <div>
          <p className="summary-label">Preferred learning style</p>
          <p>{learningStyle}</p>
        </div>
        <div>
          <p className="summary-label">Account status</p>
          <p>Active</p>
        </div>
        <div>
          <p className="summary-label">Member since</p>
          <p>{memberSince}</p>
        </div>
      </div>
    </Card>
  )
}
