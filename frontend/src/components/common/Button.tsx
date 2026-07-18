import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
  isLoading?: boolean
}

export const Button = ({ children, variant = 'primary', isLoading, className = '', ...props }: ButtonProps) => {
  const variantClass = variant === 'secondary' 
    ? 'button-secondary' 
    : variant === 'outline' 
      ? 'px-4 py-2 text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-600 dark:hover:bg-slate-700'
      : 'button-primary';
      
  return (
    <button className={`button ${variantClass} ${className} flex items-center justify-center gap-2`} {...props}>
      {isLoading && (
        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
}
