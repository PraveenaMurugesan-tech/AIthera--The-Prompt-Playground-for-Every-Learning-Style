import { useNavigate } from 'react-router-dom';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { RecordingIndicator } from './RecordingIndicator';
import { UnsupportedBrowser } from './UnsupportedBrowser';
import { VoiceControls } from './VoiceControls';
import { VoiceTranscript } from './VoiceTranscript';
import { AlertCircle } from 'lucide-react';

export const VoiceRecorder = () => {
  const {
    isSupported,
    transcript,
    interimTranscript,
    listeningState,
    error,
    startListening,
    stopListening,
    clearTranscript,
    setTranscript
  } = useSpeechRecognition();
  
  const navigate = useNavigate();

  if (!isSupported) {
    return <UnsupportedBrowser />;
  }

  const handleSendToGenerator = (text: string) => {
    navigate('/loading', { 
      state: { 
        formData: {
          topic: text,
          learningStyle: 'conversational', // Default for voice
          difficulty: 'beginner',
          bloomLevel: 'understand',
          instructions: 'Generated from Voice Recording'
        }
      } 
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Voice Input</h2>
        <RecordingIndicator isRecording={listeningState === 'listening'} />
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg flex items-center gap-2 border border-red-200 dark:border-red-800">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-6 items-start h-[300px]">
        <VoiceTranscript 
          transcript={transcript}
          interimTranscript={interimTranscript}
          onChange={setTranscript}
          onSendToGenerator={handleSendToGenerator}
        />
        
        <div className="flex md:flex-col justify-center items-center gap-4 bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 h-full shadow-sm">
          <VoiceControls 
            mode="record"
            isRecording={listeningState === 'listening'}
            onStart={startListening}
            onStop={stopListening}
            onClear={clearTranscript}
          />
        </div>
      </div>
    </div>
  );
};
