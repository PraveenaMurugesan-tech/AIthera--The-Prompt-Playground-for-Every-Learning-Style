import { Card } from '../common/Card'

type ProgressMetric = {
  label: string
  value: number
  suffix?: string
}

const progressMetrics: ProgressMetric[] = [
  { label: 'Prompts generated', value: 24, suffix: 'prompts' },
  { label: 'Learning sessions', value: 8, suffix: 'sessions' },
  { label: 'Favorite topics', value: 5, suffix: 'topics' },
]

export const LearningProgressCard = () => {
  return (
    <Card title="Learning progress">
      <div className="progress-stack">
        {progressMetrics.map((metric) => (
          <div key={metric.label} className="metric-card">
            <div className="metric-header">
              <span>{metric.label}</span>
              <strong>{metric.value} {metric.suffix}</strong>
            </div>
            <div className="progress-bar" aria-hidden="true">
              <div className="progress-fill" style={{ width: `${Math.min(metric.value * 8, 100)}%` }} />
            </div>
          </div>
        ))}
        <div className="metric-card">
          <div className="metric-header">
            <span>Completion percentage</span>
            <strong>78%</strong>
          </div>
          <div className="progress-bar" aria-hidden="true">
            <div className="progress-fill" style={{ width: '78%' }} />
          </div>
        </div>
      </div>
    </Card>
  )
}
