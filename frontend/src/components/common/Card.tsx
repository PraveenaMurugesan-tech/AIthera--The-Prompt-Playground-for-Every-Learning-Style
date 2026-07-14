import type { ReactNode } from 'react'

type CardProps = {
  title?: string
  children: ReactNode
}

export const Card = ({ title, children }: CardProps) => {
  return (
    <section className="card">
      {title ? <h3>{title}</h3> : null}
      <div>{children}</div>
    </section>
  )
}
