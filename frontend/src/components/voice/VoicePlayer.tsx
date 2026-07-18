import { useState } from 'react';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { VoiceControls } from './VoiceControls';
import { VoiceSettings } from './VoiceSettings';
import { Volume2, AlertCircle } from 'lucide-react';

export const VoicePlayer = () => {
  const {
    isSupported,
    voices,
    settings,
    updateSettings,
    speakingState,
    error,
    speak,
    pause,
    resume,
    stop
  } = useSpeechSynthesis();

  const [textToRead, setTextToRead] = useState(
    "Welcome to AIthera Voice Learning. I can read generated prompts and AI responses aloud. You can customize my voice, pitch, and speed using the settings below."
  );

  if (!isSupported) {
    return null; // Don't show player if synthesis isn't supported, recorder will show UnsupportedBrowser
  }

  return (
    <div className="flex flex-col gap-6 text-slate-900 dark:text-slate-100">
      <div className="flex items-center gap-2">
        <Volume2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        <h2 className="text-2xl font-bold">Text-to-Speech</h2>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg flex items-center gap-2 border border-red-200 dark:border-red-800">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm flex flex-col h-full min-h-[200px]">
            <div className="p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
              <h3 className="font-semibold text-sm">Text to Read</h3>
            </div>
            <textarea
              value={textToRead}
              onChange={(e) => setTextToRead(e.target.value)}
              className="flex-1 w-full p-4 bg-transparent resize-none outline-none text-slate-900 dark:text-slate-100"
              placeholder="Enter text to be read aloud..."
            />
          </div>
          
          <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 flex justify-center shadow-sm">
            <VoiceControls
              mode="speak"
              isSpeaking={speakingState === 'speaking' || speakingState === 'paused'}
              isPaused={speakingState === 'paused'}
              onStart={() => speak(textToRead)}
              onPause={pause}
              onResume={resume}
              onStop={stop}
            />
          </div>
        </div>

        <div className="lg:col-span-1">
          <VoiceSettings 
            settings={settings}
            voices={voices}
            onChange={updateSettings}
          />
        </div>
      </div>
    </div>
  );
};
