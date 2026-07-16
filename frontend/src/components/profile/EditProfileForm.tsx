import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from 'react'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../common/Button'
import { Card } from '../common/Card'
import { useToast } from '../../context/ToastContext'

type ProfileFormState = {
  name: string
  email: string
  learningStyle: string
  difficulty: string
  bio: string
}

const initialState: ProfileFormState = {
  name: '',
  email: '',
  learningStyle: 'Adaptive',
  difficulty: 'Intermediate',
  bio: 'I enjoy learning through examples and structured practice.',
}

export const EditProfileForm = () => {
  const { currentUser } = useAuth()
  const { showToast } = useToast()
  const [form, setForm] = useState<ProfileFormState>(initialState)
  const [message, setMessage] = useState<string>('')
  const [isSaved, setIsSaved] = useState(false)

  const storageKey = 'aithera-profile-form'

  useEffect(() => {
    const stored = window.localStorage.getItem(storageKey)
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ProfileFormState
        setForm(parsed)
      } catch {
        // Ignore malformed saved data and fall back to defaults.
      }
    }
  }, [])

  useEffect(() => {
    setForm((current) => ({
      ...current,
      name: currentUser?.name || current.name,
      email: currentUser?.email || current.email,
    }))
  }, [currentUser])

  const validationMessage = useMemo(() => {
    if (!form.name.trim()) {
      return 'Your name is required.'
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      return 'Please enter a valid email address.'
    }
    return ''
  }, [form.email, form.name])

  const handleChange = (field: keyof ProfileFormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage('')
    setIsSaved(false)
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (validationMessage) {
      setMessage(validationMessage)
      setIsSaved(false)
      showToast(validationMessage, 'error')
      return
    }

    window.localStorage.setItem(storageKey, JSON.stringify(form))
    setMessage('Profile updated successfully.')
    setIsSaved(true)
    showToast('Profile updated successfully.', 'success')
    // TODO: Replace this mock persistence with a real PATCH /profile endpoint when available.
  }

  return (
    <Card title="Edit profile">
      <form className="settings-form" onSubmit={handleSubmit} noValidate>
        <label className="field">
          <span>Name</span>
          <input value={form.name} onChange={(event: ChangeEvent<HTMLInputElement>) => handleChange('name', event.target.value)} />
        </label>

        <label className="field">
          <span>Email</span>
          <input type="email" value={form.email} onChange={(event: ChangeEvent<HTMLInputElement>) => handleChange('email', event.target.value)} />
        </label>

        <label className="field">
          <span>Learning style</span>
          <input value={form.learningStyle} onChange={(event: ChangeEvent<HTMLInputElement>) => handleChange('learningStyle', event.target.value)} />
        </label>

        <label className="field">
          <span>Difficulty</span>
          <input value={form.difficulty} onChange={(event: ChangeEvent<HTMLInputElement>) => handleChange('difficulty', event.target.value)} />
        </label>

        <label className="field">
          <span>Short bio</span>
          <textarea value={form.bio} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => handleChange('bio', event.target.value)} rows={3} />
        </label>

        {message ? <div className={`status-banner ${isSaved ? 'success' : 'error'}`}>{message}</div> : null}

        <Button type="submit">Save profile</Button>
      </form>
    </Card>
  )
}
