import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
  variant?: 'primary' | 'secondary'
}

export const Button = ({ children, variant = 'primary', ...props }: ButtonProps) => {
  const variantClass = variant === 'secondary' ? 'button-secondary' : 'button-primary'

  return (
    <button className={`button ${variantClass}`} {...props}>
      {children}
    </button>
  )
}
