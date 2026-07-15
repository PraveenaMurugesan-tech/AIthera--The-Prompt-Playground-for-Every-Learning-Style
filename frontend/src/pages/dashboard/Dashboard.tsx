import { CouncilStatusCard } from '../../components/dashboard/CouncilStatusCard'
import { DashboardHeader } from '../../components/dashboard/DashboardHeader'
import { LearningProgressCard } from '../../components/dashboard/LearningProgressCard'
import { ProfileSummaryCard } from '../../components/dashboard/ProfileSummaryCard'
import { QuickActions } from '../../components/dashboard/QuickActions'
import { RecentActivity } from '../../components/dashboard/RecentActivity'
import { RecommendationsCard } from '../../components/dashboard/RecommendationsCard'
import { WelcomeCard } from '../../components/dashboard/WelcomeCard'

export const DashboardPage = () => {
  return (
    <div className="dashboard-page">
      <DashboardHeader />
      <div className="dashboard-grid">
        <div className="dashboard-main-column">
          <WelcomeCard />
          <QuickActions />
          <div className="dashboard-grid-inner">
            <CouncilStatusCard />
            <LearningProgressCard />
          </div>
        </div>
        <div className="dashboard-side-column">
          <ProfileSummaryCard />
          <RecentActivity />
          <RecommendationsCard />
        </div>
      </div>
    </div>
  )
}
