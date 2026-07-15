import { Card } from '../common/Card'

type ProviderStatus = {
  name: string
  status: 'Ready' | 'Pending'
}

const providers: ProviderStatus[] = [
  { name: 'ChatGPT', status: 'Ready' },
  { name: 'Claude', status: 'Ready' },
  { name: 'Gemini', status: 'Ready' },
  { name: 'DeepSeek', status: 'Ready' },
]

export const CouncilStatusCard = () => {
  return (
    <Card title="AI council">
      <div className="status-list">
        {providers.map((provider) => (
          <div key={provider.name} className="status-row">
            <span>{provider.name}</span>
            <span className="status-pill">{provider.status}</span>
          </div>
        ))}
      </div>
      <div className="status-summary">
        <strong>Overall status:</strong> Ready to generate prompts
      </div>
    </Card>
  )
}
