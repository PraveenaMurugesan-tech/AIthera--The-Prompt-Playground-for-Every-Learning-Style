import { EditProfileForm } from '../../components/profile/EditProfileForm'
import { ProfileDetailsCard } from '../../components/profile/ProfileDetailsCard'
import { ProfileOverviewCard } from '../../components/profile/ProfileOverviewCard'

export const ProfilePage = () => {
  return (
    <div className="profile-page">
      <ProfileOverviewCard />
      <EditProfileForm />
      <div className="profile-grid">
        <ProfileDetailsCard title="Learning preferences">
          <div className="detail-card-block">
            <span className="summary-label">Primary style</span>
            <strong>Visual + Example-led</strong>
          </div>
          <div className="detail-card-block">
            <span className="summary-label">Preferred difficulty</span>
            <strong>Intermediate</strong>
          </div>
          <div className="detail-card-block">
            <span className="summary-label">Study cadence</span>
            <strong>Daily</strong>
          </div>
        </ProfileDetailsCard>
        <ProfileDetailsCard title="Account information">
          <div className="detail-card-block">
            <span className="summary-label">Account status</span>
            <strong>Active</strong>
          </div>
          <div className="detail-card-block">
            <span className="summary-label">Last sign in</span>
            <strong>Today</strong>
          </div>
          <div className="detail-card-block">
            <span className="summary-label">Security</span>
            <strong>Protected</strong>
          </div>
        </ProfileDetailsCard>
      </div>
    </div>
  )
}
