import { useState, useEffect, useCallback } from 'react';
import { voiceService } from '../services/voiceService';
import type { SpeakingState, VoiceSettings } from '../types/voice';

const DEFAULT_SETTINGS: VoiceSettings = {
  voiceURI: null,
  pitch: 1,
  rate: 1,
  volume: 1,
  lang: 'en-US'
};

export function useSpeechSynthesis() {
  const [isSupported, setIsSupported] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [settings, setSettings] = useState<VoiceSettings>(() => {
    const saved = localStorage.getItem('aithera_voice_settings');
    if (saved) {
      try {
        return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
      } catch (e) {
        return DEFAULT_SETTINGS;
      }
    }
    return DEFAULT_SETTINGS;
  });
  const [speakingState, setSpeakingState] = useState<SpeakingState>('idle');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsSupported(voiceService.isSynthesisSupported());

    if (voiceService.isSynthesisSupported()) {
      const loadVoices = () => {
        const availableVoices = voiceService.getAvailableVoices();
        setVoices(availableVoices);
        if (availableVoices.length > 0 && !settings.voiceURI) {
          // Set default voice if none selected
          const defaultVoice = availableVoices.find(v => v.default) || availableVoices[0];
          setSettings(prev => ({ ...prev, voiceURI: defaultVoice.voiceURI }));
        }
      };

      loadVoices();
      
      // Voices are sometimes loaded asynchronously
      if (typeof window.speechSynthesis !== 'undefined') {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }

      return () => {
        if (typeof window.speechSynthesis !== 'undefined') {
          window.speechSynthesis.onvoiceschanged = null;
        }
      };
    }
  }, [settings.voiceURI]);

  useEffect(() => {
    localStorage.setItem('aithera_voice_settings', JSON.stringify(settings));
  }, [settings]);

  const speak = useCallback((text: string) => {
    if (!voiceService.isSynthesisSupported()) {
      setError('Browser not supported');
      return;
    }
    
    setError(null);
    setSpeakingState('speaking');
    
    const utterance = voiceService.speak(text, settings);
    
    if (utterance) {
      utterance.onend = () => setSpeakingState('idle');
      utterance.onerror = (e) => {
        console.error('Synthesis error:', e);
        setError('Error during speech playback');
        setSpeakingState('error');
      };
      utterance.onpause = () => setSpeakingState('paused');
      utterance.onresume = () => setSpeakingState('speaking');
    }
  }, [settings]);

  const pause = useCallback(() => {
    voiceService.pauseSpeaking();
    setSpeakingState('paused');
  }, []);

  const resume = useCallback(() => {
    voiceService.resumeSpeaking();
    setSpeakingState('speaking');
  }, []);

  const stop = useCallback(() => {
    voiceService.stopSpeaking();
    setSpeakingState('idle');
  }, []);

  const updateSettings = useCallback((newSettings: Partial<VoiceSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  return {
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
  };
}
