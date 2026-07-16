// Types for standardizing the Web Speech API

export class VoiceService {
  private recognition: any = null;
  private synthesis: SpeechSynthesis = window.speechSynthesis;
  
  constructor() {
    this.initRecognition();
  }

  private initRecognition() {
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
    }
  }

  public isRecognitionSupported(): boolean {
    return this.recognition !== null;
  }

  public isSynthesisSupported(): boolean {
    return 'speechSynthesis' in window;
  }

  public getRecognition() {
    return this.recognition;
  }

  public getSynthesis() {
    return this.synthesis;
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    if (!this.isSynthesisSupported()) return [];
    return this.synthesis.getVoices();
  }

  private currentUtterance: SpeechSynthesisUtterance | null = null;

  public speak(text: string, options?: { voiceURI?: string | null, pitch?: number, rate?: number, volume?: number, lang?: string }) {
    if (!this.isSynthesisSupported() || !text) return;

    if (this.synthesis.speaking || this.synthesis.pending) {
      this.synthesis.cancel();
    }

    this.currentUtterance = new SpeechSynthesisUtterance(text);
    
    if (options) {
      if (options.pitch !== undefined) this.currentUtterance.pitch = options.pitch;
      if (options.rate !== undefined) this.currentUtterance.rate = options.rate;
      if (options.volume !== undefined) this.currentUtterance.volume = options.volume;
      if (options.lang) this.currentUtterance.lang = options.lang;
      
      if (options.voiceURI) {
        const voices = this.getAvailableVoices();
        const selectedVoice = voices.find(v => v.voiceURI === options.voiceURI);
        if (selectedVoice) {
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
