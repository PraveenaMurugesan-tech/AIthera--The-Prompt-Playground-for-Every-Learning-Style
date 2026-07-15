import { Card } from '../common/Card'

type Recommendation = {
  title: string
  description: string
}

const recommendations: Recommendation[] = [
  { title: 'Practice React', description: 'Build a small component and review the feedback loop.' },
  { title: 'Learn system design', description: 'Focus on scalability patterns and design tradeoffs.' },
  { title: 'Improve prompt engineering', description: 'Refine clarity, constraints, and expected output.' },
]

export const RecommendationsCard = () => {
  return (
    <Card title="Learning recommendations">
      <div className="recommendations-list">
        {recommendations.map((item) => (
          <div key={item.title} className="recommendation-item">
            <strong>{item.title}</strong>
            <p>{item.description}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}
