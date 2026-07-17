import { Card } from '../common/Card'

type ProfileDetailsCardProps = {
  title?: string
  children: React.ReactNode
}

export const ProfileDetailsCard = ({ title, children }: ProfileDetailsCardProps) => {
  return (
    <Card title={title}>
      <div className="profile-details-grid">{children}</div>
    </Card>
  )
}
