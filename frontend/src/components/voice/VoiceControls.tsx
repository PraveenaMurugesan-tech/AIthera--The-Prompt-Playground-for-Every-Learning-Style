import { Play, Square, Pause, Mic, MicOff, Trash2 } from 'lucide-react';

interface VoiceControlsProps {
  onStart?: () => void;
  onStop?: () => void;
  onPause?: () => void;
  onResume?: () => void;
  onClear?: () => void;
  
  isRecording?: boolean;
  isSpeaking?: boolean;
  isPaused?: boolean;
  
  mode: 'record' | 'speak';
}

export const VoiceControls = ({
  onStart,
  onStop,
  onPause,
  onResume,
  onClear,
  isRecording,
  isSpeaking,
  isPaused,
  mode
}: VoiceControlsProps) => {
  
  return (
    <div className="flex items-center gap-2">
      {mode === 'record' ? (
        <>
          {!isRecording ? (
            <button
              onClick={onStart}
              className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors shadow-sm flex items-center gap-2 px-6"
              title="Start Recording"
            >
              <Mic className="w-5 h-5" />
              <span className="font-semibold">Record</span>
            </button>
          ) : (
            <button
              onClick={onStop}
              className="p-3 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors shadow-sm flex items-center gap-2 px-6"
              title="Stop Recording"
            >
              <MicOff className="w-5 h-5" />
            </button>
          )}
        </>
      ) : (
        <>
          {!isSpeaking ? (
            <button
              onClick={onStart}
              className="p-3 bg-slate-500 text-white rounded-full hover:bg-slate-600 transition-colors shadow-sm"
              title="Play"
            >
              <Play className="w-5 h-5" />
            </button>
          ) : (
            <>
              {isPaused ? (
                <button
                  onClick={onResume}
                  className="p-3 bg-yellow-500 text-white rounded-full hover:bg-yellow-600 transition-colors shadow-sm"
                  title="Resume"
                >
                  <Play className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={onPause}
                  className="p-3 bg-yellow-500 text-white rounded-full hover:bg-yellow-600 transition-colors shadow-sm"
                  title="Pause"
                >
                  <Pause className="w-5 h-5" />
                </button>
              )}
              <button
                onClick={onStop}
                className="p-3 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors shadow-sm"
                title="Stop"
              >
                <Square className="w-5 h-5" />
              </button>
            </>
          )}
        </>
      )}

      {onClear && (
        <button
          onClick={onClear}
          className="p-3 text-slate-500 hover:text-red-500 dark:text-slate-400 dark:hover:text-red-400 transition-colors ml-auto"
          title="Clear"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};
