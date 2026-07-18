import { Settings2 } from 'lucide-react';
import type { VoiceSettings as VoiceSettingsType } from '../../types/voice';

interface VoiceSettingsProps {
  settings: VoiceSettingsType;
  voices: SpeechSynthesisVoice[];
  onChange: (settings: Partial<VoiceSettingsType>) => void;
}

export const VoiceSettings = ({ settings, voices, onChange }: VoiceSettingsProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 shadow-sm text-slate-900 dark:text-slate-100">
      <div className="flex items-center gap-2 mb-4">
        <Settings2 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h3 className="font-semibold">Voice Settings</h3>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Voice</label>
          <select 
            className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-600 outline-none transition-shadow text-slate-900 dark:text-slate-100"
            value={settings.voiceURI || ''}
            onChange={(e) => onChange({ voiceURI: e.target.value })}
          >
            {voices.map(voice => (
              <option key={voice.voiceURI} value={voice.voiceURI}>
                {voice.name} ({voice.lang})
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <div className="flex justify-between text-sm mb-1">
            <label className="font-medium">Speed</label>
            <span className="text-slate-500 dark:text-slate-400">{settings.rate}x</span>
          </div>
          <input 
            type="range" 
            min="0.5" max="2" step="0.1" 
            value={settings.rate}
            onChange={(e) => onChange({ rate: parseFloat(e.target.value) })}
            className="w-full accent-blue-600"
          />
        </div>
        
        <div>
          <div className="flex justify-between text-sm mb-1">
            <label className="font-medium">Pitch</label>
            <span className="text-slate-500 dark:text-slate-400">{settings.pitch}</span>
          </div>
          <input 
            type="range" 
            min="0" max="2" step="0.1" 
            value={settings.pitch}
            onChange={(e) => onChange({ pitch: parseFloat(e.target.value) })}
            className="w-full accent-blue-600"
          />
        </div>
        
        <div>
          <div className="flex justify-between text-sm mb-1">
            <label className="font-medium">Volume</label>
            <span className="text-slate-500 dark:text-slate-400">{Math.round(settings.volume * 100)}%</span>
          </div>
          <input 
            type="range" 
            min="0" max="1" step="0.1" 
            value={settings.volume}
            onChange={(e) => onChange({ volume: parseFloat(e.target.value) })}
            className="w-full accent-blue-600"
          />
        </div>
      </div>
    </div>
  );
};
