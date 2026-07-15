import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../common/Button'
import { Card } from '../common/Card'

type LoginFormProps = {
  onSuccess?: () => void
}

type FormState = {
  email: string
  password: string
  rememberMe: boolean
}

const initialState: FormState = {
  email: '',
  password: '',
  rememberMe: false,
}

export const LoginForm = ({ onSuccess }: LoginFormProps) => {
  const [form, setForm] = useState<FormState>(initialState)
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({})
  const [showPassword, setShowPassword] = useState(false)
  const [status, setStatus] = useState<'idle' | 'loading' | 'error' | 'success'>('idle')
  const [message, setMessage] = useState('')
  const { login, loading, error, clearError, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  useEffect(() => {
    return () => clearError()
  }, [clearError])

  const validate = useMemo(() => {
    return () => {
      const nextErrors: Partial<Record<keyof FormState, string>> = {}

      if (!form.email.trim()) {
        nextErrors.email = 'Email is required.'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        nextErrors.email = 'Enter a valid email address.'
      }

      if (!form.password) {
        nextErrors.password = 'Password is required.'
      }

      return nextErrors
    }
  }, [form.email, form.password])

  const handleChange = (field: keyof FormState, value: string | boolean) => {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
    if (message) {
      setMessage('')
    }
    if (error) {
      clearError()
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const nextErrors = validate()
    setErrors(nextErrors)

    if (Object.keys(nextErrors).length > 0) {
      return
    }

    setStatus('loading')
    setMessage('')

    try {
      await login({
        email: form.email.trim(),
        password: form.password,
        rememberMe: form.rememberMe,
      })
      setStatus('success')
      setMessage('Login successful.')
      onSuccess?.()
      navigate('/dashboard', { replace: true })
    } catch (submissionError) {
      setStatus('error')
      setMessage(submissionError instanceof Error ? submissionError.message : 'Unable to sign in. Please try again.')
    }
  }

  const isSubmitting = loading || status === 'loading'

  return (
    <div className="page-shell">
      <Card title="Welcome back">
        <p className="muted">Access your learning workspace.</p>
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={(event) => handleChange('email', event.target.value)}
              aria-invalid={Boolean(errors.email)}
              disabled={isSubmitting}
            />
            {errors.email ? <small className="field-error">{errors.email}</small> : null}
          </label>

          <label className="field">
            <span>Password</span>
            <div className="password-field">
              <input
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={form.password}
                onChange={(event) => handleChange('password', event.target.value)}
                aria-invalid={Boolean(errors.password)}
                disabled={isSubmitting}
              />
              <button type="button" className="ghost-button" onClick={() => setShowPassword((current) => !current)} disabled={isSubmitting}>
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            {errors.password ? <small className="field-error">{errors.password}</small> : null}
          </label>

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={form.rememberMe}
              onChange={(event) => handleChange('rememberMe', event.target.checked)}
              disabled={isSubmitting}
            />
            <span>Remember me</span>
          </label>

          {message ? <div className={`status-banner ${status}`} aria-live="polite">{message}</div> : null}
          {error ? <div className="status-banner error" aria-live="polite">{error}</div> : null}

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>

        <div className="page-actions">
          <span className="muted">New here?</span>
          <Link to="/register">Create an account</Link>
        </div>
      </Card>
    </div>
  )
}
