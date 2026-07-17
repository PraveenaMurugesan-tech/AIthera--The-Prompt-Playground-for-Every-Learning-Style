import { SettingsFormCard } from '../../components/settings/SettingsFormCard'
import { SettingsProfileCard } from '../../components/settings/SettingsProfileCard'

export const SettingsPage = () => {
  return (
    <div className="settings-page">
      <SettingsProfileCard />
      <SettingsFormCard />
    </div>
  )
}
