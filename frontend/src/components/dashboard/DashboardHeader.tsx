import { useMemo } from 'react'
import { useAuth } from '../../context/AuthContext'

type DashboardHeaderProps = {
  title?: string
}

export const DashboardHeader = ({ title = 'Dashboard' }: DashboardHeaderProps) => {
  const { currentUser } = useAuth()

  const today = useMemo(() => new Date().toLocaleDateString('en', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }), [])

  return (
    <section className="dashboard-header">
      <div>
        <p className="eyebrow">Learning dashboard</p>
        <h2>{title}</h2>
        <p className="muted">Welcome back, {currentUser?.name || currentUser?.email || 'there'}.</p>
      </div>
      <div className="dashboard-date-pill">
        <span>{today}</span>
      </div>
    </section>
  )
}
