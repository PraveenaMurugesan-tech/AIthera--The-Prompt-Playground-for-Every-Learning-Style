import { Card } from '../common/Card'

type ActivityItem = {
  title: string
  detail: string
}

const activities: ActivityItem[] = [
  { title: 'Generated Python prompt', detail: '2 hours ago' },
  { title: 'Viewed AI explanation', detail: 'Yesterday' },
  { title: 'Updated learning style', detail: '3 days ago' },
]

export const RecentActivity = () => {
  return (
    <Card title="Recent activity">
      <ul className="activity-list">
        {activities.map((activity) => (
          <li key={activity.title}>
            <strong>{activity.title}</strong>
            <span>{activity.detail}</span>
          </li>
        ))}
      </ul>
    </Card>
  )
}
