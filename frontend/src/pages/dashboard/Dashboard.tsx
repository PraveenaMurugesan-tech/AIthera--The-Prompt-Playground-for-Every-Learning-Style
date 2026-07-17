import { Card } from '../../components/common/Card'
import { usePerformanceMonitor } from '../../hooks/usePerformanceMonitor'

export const DashboardPage = () => {
  usePerformanceMonitor('DashboardPage')
  
  return (
    <div className="page-shell">
      <Card title="Dashboard">
        <p>Your upcoming learning experience will appear here.</p>
      </Card>
    </div>
  )
}
