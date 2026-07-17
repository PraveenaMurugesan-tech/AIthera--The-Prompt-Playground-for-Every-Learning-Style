import { Card } from '../common/Card'

type PreferenceFieldProps = {
  label: string
  description: string
}

const PreferenceField = ({ label, description }: PreferenceFieldProps) => (
  <label className="settings-field">
    <div>
      <strong>{label}</strong>
      <p>{description}</p>
    </div>
    <input type="checkbox" defaultChecked />
  </label>
)

export const SettingsPreferencesCard = () => {
  return (
    <Card title="Preferences">
      <div className="settings-list">
        <PreferenceField label="Dark mode" description="Use the darker theme by default." />
        <PreferenceField label="Learning reminders" description="Receive gentle reminders for daily study." />
        <PreferenceField label="Prompt suggestions" description="Get curated idea prompts after each session." />
      </div>
    </Card>
  )
}
