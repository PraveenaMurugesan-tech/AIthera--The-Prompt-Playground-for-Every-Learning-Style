import { Card } from '../common/Card'

type SettingItemProps = {
  label: string
  value: string
}

const SettingItem = ({ label, value }: SettingItemProps) => (
  <div className="settings-item">
    <span>{label}</span>
    <strong>{value}</strong>
  </div>
)

export const SettingsProfileCard = () => {
  return (
    <Card title="Account settings">
      <div className="settings-list">
        <SettingItem label="Learning style" value="Adaptive" />
        <SettingItem label="Difficulty" value="Intermediate" />
        <SettingItem label="Voice preference" value="Narrator" />
        <SettingItem label="Privacy" value="Private" />
      </div>
    </Card>
  )
}
