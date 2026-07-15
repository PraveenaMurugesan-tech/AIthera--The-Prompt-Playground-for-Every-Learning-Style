import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../common/Button'
import { Card } from '../common/Card'

type RegisterFormProps = {
  onSuccess?: () => void
}

type FormState = {
  name: string
  email: string
  password: string
  confirmPassword: string
}

const initialState: FormState = {
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
}

export const RegisterForm = ({ onSuccess }: RegisterFormProps) => {
  const [form, setForm] = useState<FormState>(initialState)
  const [errors, setErrors] = useState<Partial<Record<keyof FormState, string>>>({})
  const [status, setStatus] = useState<'idle' | 'loading' | 'error' | 'success'>('idle')
  const [message, setMessage] = useState('')
  const { register, loading, error, clearError, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const validate = useMemo(() => {
    return () => {
      const nextErrors: Partial<Record<keyof FormState, string>> = {}

      if (!form.name.trim()) {
        nextErrors.name = 'Name is required.'
      }

      if (!form.email.trim()) {
        nextErrors.email = 'Email is required.'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        nextErrors.email = 'Enter a valid email address.'
      }

      if (!form.password) {
        nextErrors.password = 'Password is required.'
      } else if (form.password.length < 8) {
        nextErrors.password = 'Password must be at least 8 characters.'
      }

      if (!form.confirmPassword) {
        nextErrors.confirmPassword = 'Please confirm your password.'
      } else if (form.confirmPassword !== form.password) {
        nextErrors.confirmPassword = 'Passwords do not match.'
      }

      return nextErrors
    }
  }, [form.confirmPassword, form.email, form.name, form.password])

  const handleChange = (field: keyof FormState, value: string) => {
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
      await register({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      setStatus('success')
      setMessage('Registration successful. Please login.')
      onSuccess?.()
      setTimeout(() => navigate('/login', { replace: true }), 1200)
    } catch (submissionError) {
      setStatus('error')
      setMessage(submissionError instanceof Error ? submissionError.message : 'Unable to create your account right now.')
    }
  }

  const isSubmitting = loading || status === 'loading'

  return (
    <div className="page-shell">
      <Card title="Create your account">
        <p className="muted">Start your AI Thera journey.</p>
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label className="field">
            <span>Name</span>
            <input
              type="text"
              autoComplete="name"
              value={form.name}
              onChange={(event) => handleChange('name', event.target.value)}
              aria-invalid={Boolean(errors.name)}
              disabled={isSubmitting}
            />
            {errors.name ? <small className="field-error">{errors.name}</small> : null}
          </label>

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
            <input
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={(event) => handleChange('password', event.target.value)}
              aria-invalid={Boolean(errors.password)}
              disabled={isSubmitting}
            />
            {errors.password ? <small className="field-error">{errors.password}</small> : null}
          </label>

          <label className="field">
            <span>Confirm password</span>
            <input
              type="password"
              autoComplete="new-password"
              value={form.confirmPassword}
              onChange={(event) => handleChange('confirmPassword', event.target.value)}
              aria-invalid={Boolean(errors.confirmPassword)}
              disabled={isSubmitting}
            />
            {errors.confirmPassword ? <small className="field-error">{errors.confirmPassword}</small> : null}
          </label>

          {message ? <div className={`status-banner ${status}`} aria-live="polite">{message}</div> : null}
          {error ? <div className="status-banner error" aria-live="polite">{error}</div> : null}

          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Registering…' : 'Create account'}
          </Button>
        </form>

        <div className="page-actions">
          <span className="muted">Already have an account?</span>
          <Link to="/login">Sign in</Link>
        </div>
      </Card>
    </div>
  )
}
