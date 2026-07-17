import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Button } from '../common/Button'
import { Card } from '../common/Card'
import { useTheme } from '../../context/ThemeContext'
import { useToast } from '../../context/ToastContext'

type SettingsFormState = {
  notifications: boolean
  reminders: boolean
  suggestions: boolean
  compactMode: boolean
}

const storageKey = 'aithera-settings-form'

export const SettingsFormCard = () => {
  const { theme, toggleTheme } = useTheme()
  const { showToast } = useToast()
  const [settings, setSettings] = useState<SettingsFormState>({
    notifications: true,
    reminders: true,
    suggestions: true,
    compactMode: false,
  })
  const [message, setMessage] = useState('')

  useEffect(() => {
    const stored = window.localStorage.getItem(storageKey)
    if (!stored) {
      return
    }
    try {
      const parsed = JSON.parse(stored) as SettingsFormState
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setSettings(parsed)
    } catch {
      // Ignore malformed saved data and keep defaults.
    }
  }, [])

  const summary = useMemo(() => {
    const enabled = Object.values(settings).filter(Boolean).length
    return `${enabled} preference${enabled === 1 ? '' : 's'} active`
  }, [settings])

  const handleToggle = (field: keyof SettingsFormState) => {
    setSettings((current) => ({ ...current, [field]: !current[field] }))
    setMessage('Preferences updated.')
    showToast('Preferences updated.', 'info')
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    window.localStorage.setItem(storageKey, JSON.stringify(settings))
    setMessage('Preferences saved locally.')
    showToast('Preferences saved successfully!', 'success')
  }

  return (
    <Card title="Preferences" subtitle={summary}>
      <form className="settings-form" onSubmit={handleSubmit}>
        <label className="toggle-row">
          <span>Enable notifications</span>
          <input type="checkbox" checked={settings.notifications} onChange={() => handleToggle('notifications')} />
        </label>

        <label className="toggle-row">
          <span>Weekly reminders</span>
          <input type="checkbox" checked={settings.reminders} onChange={() => handleToggle('reminders')} />
        </label>

        <label className="toggle-row">
          <span>Suggested next steps</span>
          <input type="checkbox" checked={settings.suggestions} onChange={() => handleToggle('suggestions')} />
        </label>

        <label className="toggle-row">
          <span>Compact dashboard</span>
          <input type="checkbox" checked={settings.compactMode} onChange={() => handleToggle('compactMode')} />
        </label>

        <label className="toggle-row">
          <span>Theme: {theme === 'dark' ? 'Dark' : 'Light'}</span>
          <button type="button" className="ghost-button" onClick={toggleTheme}>
            Switch theme
          </button>
        </label>

        {message ? <div className="status-banner success">{message}</div> : null}

        <Button type="submit">Save preferences</Button>
      </form>
    </Card>
  )
}
