import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'

export const NotFoundPage = () => {
  return (
    <div className="page-shell not-found-shell">
      <Card title="404">
        <p>The page you are looking for could not be found.</p>
        <div className="page-actions">
          <Link to="/dashboard">
            <Button>Return to dashboard</Button>
          </Link>
        </div>
      </Card>
    </div>
  )
}
