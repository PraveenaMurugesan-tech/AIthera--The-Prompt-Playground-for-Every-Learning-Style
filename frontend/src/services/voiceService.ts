// Types for standardizing the Web Speech API

// Basic type definitions for the Web Speech API
export interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

export interface SpeechRecognitionResultList {
  readonly length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

export interface SpeechRecognitionResult {
  readonly length: number;
  readonly isFinal: boolean;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

export interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}

export interface ISpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((this: ISpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
  onerror: ((this: ISpeechRecognition, ev: Event) => void) | null;
  onend: ((this: ISpeechRecognition, ev: Event) => void) | null;
  onstart: ((this: ISpeechRecognition, ev: Event) => void) | null;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => ISpeechRecognition;
    webkitSpeechRecognition?: new () => ISpeechRecognition;
  }
}

export class VoiceService {
  private recognition: ISpeechRecognition | null = null;
  private synthesis: SpeechSynthesis = window.speechSynthesis;
  
  constructor() {
    this.initRecognition();
  }

  private initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      if (this.recognition) {
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
      }
    }
  }

  public isRecognitionSupported(): boolean {
    return this.recognition !== null;
  }

  public isSynthesisSupported(): boolean {
    return 'speechSynthesis' in window;
  }

  public getRecognition(): ISpeechRecognition | null {
    return this.recognition;
  }

  public getSynthesis(): SpeechSynthesis {
    return this.synthesis;
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    if (!this.isSynthesisSupported()) return [];
    return this.synthesis.getVoices();
  }

  private currentUtterance: SpeechSynthesisUtterance | null = null;

  public speak(text: string, options?: { voiceURI?: string | null, pitch?: number, rate?: number, volume?: number, lang?: string }): SpeechSynthesisUtterance | undefined {
    if (!this.isSynthesisSupported() || !text) return;

    if (this.synthesis.speaking || this.synthesis.pending) {
      this.synthesis.cancel();
    }

    this.currentUtterance = new SpeechSynthesisUtterance(text);
    
    if (options && this.currentUtterance) {
      if (options.pitch !== undefined) this.currentUtterance.pitch = options.pitch;
      if (options.rate !== undefined) this.currentUtterance.rate = options.rate;
      if (options.volume !== undefined) this.currentUtterance.volume = options.volume;
      if (options.lang) this.currentUtterance.lang = options.lang;
      
      if (options.voiceURI) {
        const voices = this.getAvailableVoices();
        const selectedVoice = voices.find(v => v.voiceURI === options.voiceURI);
        if (selectedVoice && this.currentUtterance) {
          this.currentUtterance.voice = selectedVoice;
        }
      }
    }

    // Delay speak slightly to let cancel finish (fixes Chrome bug)
    setTimeout(() => {
      if (this.currentUtterance) {
        this.synthesis.speak(this.currentUtterance);
      }
    }, 50);

    return this.currentUtterance;
  }

  public pauseSpeaking() {
    if (this.isSynthesisSupported()) {
      this.synthesis.pause();
    }
  }

  public resumeSpeaking() {
    if (this.isSynthesisSupported()) {
      this.synthesis.resume();
    }
  }

  public stopSpeaking() {
    if (this.isSynthesisSupported()) {
      this.synthesis.cancel();
    }
  }
}

export const voiceService = new VoiceService();
