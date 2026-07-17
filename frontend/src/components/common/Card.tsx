import type { ReactNode } from 'react'

type CardProps = {
  title?: string
  subtitle?: string
  children: ReactNode
}

export const Card = ({ title, subtitle, children }: CardProps) => {
  return (
    <section className="card">
      {title ? <h3>{title}</h3> : null}
      {subtitle ? <p className="card-subtitle">{subtitle}</p> : null}
      <div>{children}</div>
    </section>
  )
}
