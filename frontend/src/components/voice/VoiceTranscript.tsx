import { Copy, Send } from 'lucide-react';

interface VoiceTranscriptProps {
  transcript: string;
  interimTranscript?: string;
  onChange?: (text: string) => void;
  onSendToGenerator?: (text: string) => void;
  readOnly?: boolean;
}

export const VoiceTranscript = ({
  transcript,
  interimTranscript,
  onChange,
  onSendToGenerator,
  readOnly = false
}: VoiceTranscriptProps) => {
  
  const handleCopy = () => {
    navigator.clipboard.writeText(transcript);
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden shadow-sm">
      <div className="flex items-center justify-between p-3 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
        <h3 className="font-semibold text-sm">Transcript</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-1.5 text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/30"
            title="Copy to clipboard"
            disabled={!transcript}
          >
            <Copy className="w-4 h-4" />
          </button>
          {onSendToGenerator && (
            <button
              onClick={() => onSendToGenerator(transcript)}
              className="p-1.5 text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 transition-colors rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/30"
              title="Send to Prompt Generator"
              disabled={!transcript}
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      <div className="relative flex-1 p-4">
        {readOnly ? (
          <div className="h-full overflow-y-auto whitespace-pre-wrap text-slate-900 dark:text-slate-100">
            {transcript || <span className="text-slate-500 dark:text-slate-400 italic">No speech detected yet...</span>}
          </div>
        ) : (
          <textarea
            value={transcript}
            onChange={(e) => onChange?.(e.target.value)}
            placeholder="Start speaking to see transcript..."
            className="w-full h-full bg-transparent resize-none outline-none text-slate-900 dark:text-slate-100"
          />
        )}
        
        {interimTranscript && (
          <div className="absolute bottom-4 left-4 right-4 text-slate-500 dark:text-slate-400 italic pointer-events-none">
            {interimTranscript}
          </div>
        )}
      </div>
    </div>
  );
};
