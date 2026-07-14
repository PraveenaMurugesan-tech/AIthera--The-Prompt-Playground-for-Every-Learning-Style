import { Link } from 'react-router-dom'
import { Button } from '../../components/common/Button'
import { Card } from '../../components/common/Card'

export const LoginPage = () => {
  return (
    <div className="page-shell">
      <Card title="Login">
        <p>Placeholder login page for Phase 1.</p>
        <div className="page-actions">
          <Button>Continue</Button>
          <Link to="/register">Create account</Link>
        </div>
      </Card>
    </div>
  )
}
