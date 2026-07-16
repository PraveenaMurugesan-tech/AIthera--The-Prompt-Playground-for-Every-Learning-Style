export interface VoiceSettings {
  voiceURI: string | null;
  pitch: number;
  rate: number;
  volume: number;
  lang: string;
}

export interface SpeechRecognitionResultType {
  transcript: string;
  isFinal: boolean;
}

export type ListeningState = 'idle' | 'listening' | 'paused' | 'error';
export type SpeakingState = 'idle' | 'speaking' | 'paused' | 'error';
