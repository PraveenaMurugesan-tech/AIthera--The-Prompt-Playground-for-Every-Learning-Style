import { useState, useEffect, useCallback, useRef } from 'react';
import { voiceService, type SpeechRecognitionEvent } from '../services/voiceService';
import type { ListeningState } from '../types/voice';

export function useSpeechRecognition() {
  const [isSupported] = useState(() => voiceService.isRecognitionSupported());
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [listeningState, setListeningState] = useState<ListeningState>('idle');
  const [error, setError] = useState<string | null>(null);

  const listeningStateRef = useRef<ListeningState>('idle');

  useEffect(() => {
    listeningStateRef.current = listeningState;
  }, [listeningState]);

  useEffect(() => {
    if (isSupported) {
      const recognition = voiceService.getRecognition();
      if (!recognition) return;
      
      recognition.onstart = () => {
        setListeningState('listening');
        setError(null);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalTrans = '';
        let interimTrans = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTrans += event.results[i][0].transcript;
          } else {
            interimTrans += event.results[i][0].transcript;
          }
        }

        if (finalTrans) {
          setTranscript(prev => prev + (prev ? ' ' : '') + finalTrans);
        }
        setInterimTranscript(interimTrans);
      };

      recognition.onerror = (event: Event & { error?: string }) => {
        console.error('Speech recognition error', event.error);
        if (event.error === 'not-allowed') {
          setError('Microphone permission denied. Please allow microphone access.');
        } else {
          setError(`Error: ${event.error}`);
        }
        setListeningState('error');
      };

      recognition.onend = () => {
        if (listeningStateRef.current === 'listening') {
          // It stopped unexpectedly (e.g., silence timeout)
          setListeningState('idle');
        }
      };
      
      return () => {
        // Cleanup if the component unmounts
        recognition.onstart = null;
        recognition.onresult = null;
        recognition.onerror = null;
        recognition.onend = null;
      };
    }
  }, [isSupported]);

  const startListening = useCallback(() => {
    if (!voiceService.isRecognitionSupported()) {
      setError('Browser not supported');
      return;
    }
    setError(null);
    try {
      const recognition = voiceService.getRecognition();
      if (recognition) {
        recognition.start();
      }
    } catch {
      // Already started or other error
    }
  }, []);

  const stopListening = useCallback(() => {
    if (voiceService.isRecognitionSupported()) {
      setListeningState('idle');
      const recognition = voiceService.getRecognition();
      if (recognition) {
        recognition.stop();
      }
      setInterimTranscript('');
    }
  }, []);

  const clearTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  const setManualTranscript = useCallback((text: string) => {
    setTranscript(text);
  }, []);

  return {
    isSupported,
    transcript,
    interimTranscript,
    listeningState,
    error,
    startListening,
    stopListening,
    clearTranscript,
    setTranscript: setManualTranscript
  };
}
