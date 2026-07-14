import { Link } from 'react-router-dom'
import { Button } from '../../components/common/Button'
import { Card } from '../../components/common/Card'

export const RegisterPage = () => {
  return (
    <div className="page-shell">
      <Card title="Register">
        <p>Placeholder registration page for Phase 1.</p>
        <div className="page-actions">
          <Button variant="secondary">Create account</Button>
          <Link to="/login">Back to login</Link>
        </div>
      </Card>
    </div>
  )
}
