import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, Plus, Image as ImageIcon, Paperclip, Search, X } from 'lucide-react';

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  onModalityChange?: (modality: 'visual' | 'conversational') => void;
  onFileSelect?: (file: File | null) => void;
  onSubmit?: () => void;
}

// Add types for SpeechRecognition since it's not standard in TypeScript DOM lib
declare global {
  interface Window {
    SpeechRecognition: unknown;
    webkitSpeechRecognition: unknown;
  }
}

export const TopicInput: React.FC<TopicInputProps> = ({ value, onChange, onModalityChange, onFileSelect, onSubmit }) => {
  const [showOptions, setShowOptions] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const menuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<unknown>(null);

  useEffect(() => {
    // Setup SpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition as unknown;
    if (SpeechRecognition) {
      recognitionRef.current = new (SpeechRecognition as new () => unknown)();
      const rec = recognitionRef.current as {
        continuous: boolean;
        interimResults: boolean;
        onresult: (event: { results: { transcript: string }[][] }) => void;
        onerror: (event: { error: string }) => void;
        onend: () => void;
      };
      rec.continuous = false;
      rec.interimResults = false;
      
      rec.onresult = (event: { results: { transcript: string }[][] }) => {
        const transcript = event.results[0][0].transcript;
        onChange(value ? `${value} ${transcript}` : transcript);
        onModalityChange?.('conversational');
        setIsListening(false);
      };
      
      rec.onerror = (event: { error: string }) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };
    }
  }, [onChange, onModalityChange, value]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowOptions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleListen = () => {
    if (isListening) {
      (recognitionRef.current as { stop: () => void })?.stop();
      setIsListening(false);
    } else {
      try {
        (recognitionRef.current as { start: () => void })?.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      onFileSelect?.(file);
      onModalityChange?.('visual');
      setShowOptions(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect?.(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="topic" className="text-sm font-medium text-slate-700 dark:text-slate-200">
        Topic
      </label>
      
      <div className="relative">
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept="image/*,.pdf,.doc,.docx,.txt"
          onChange={handleFileSelect} 
        />
        
        {showOptions && (
          <div 
            ref={menuRef} 
            className="absolute bottom-full left-0 mb-2 w-full max-w-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl z-50 p-2 flex flex-col"
          >
            <button onClick={triggerFileInput} className="flex items-center gap-3 p-3 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-left w-full transition-colors">
              <Paperclip className="h-5 w-5 text-slate-500 dark:text-slate-400" />
              <div>
                <strong className="block text-sm font-medium text-slate-900 dark:text-white">Add photos & files</strong>
                <span className="block text-xs text-slate-500 dark:text-slate-400">Upload from computer</span>
              </div>
            </button>
            <button onClick={triggerFileInput} className="flex items-center gap-3 p-3 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-left w-full transition-colors">
              <ImageIcon className="h-5 w-5 text-blue-500" />
              <div>
                <strong className="block text-sm font-medium text-slate-900 dark:text-white">Create image</strong>
                <span className="block text-xs text-slate-500 dark:text-slate-400">Visualize anything</span>
              </div>
            </button>
            <button className="flex items-center gap-3 p-3 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-left w-full transition-colors">
              <Search className="h-5 w-5 text-purple-500" />
              <div>
                <strong className="block text-sm font-medium text-slate-900 dark:text-white">Deep research</strong>
                <span className="block text-xs text-slate-500 dark:text-slate-400">Get a detailed report</span>
              </div>
            </button>
          </div>
        )}

        <div className="flex flex-col bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 transition-shadow">
          {selectedFile && (
            <div className="px-4 pt-3 pb-1">
              <div className="inline-flex items-center gap-2 bg-slate-100 dark:bg-slate-700 rounded-lg p-2 text-sm text-slate-700 dark:text-slate-300">
                <Paperclip className="h-4 w-4" />
                <span className="truncate max-w-[200px]">{selectedFile.name}</span>
                <button onClick={removeFile} className="hover:text-red-500 transition-colors">
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
          
          <div className="flex items-center pr-2">
            <button 
              type="button"
              className="pl-4 pr-3 py-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors flex items-center justify-center"
              onClick={() => setShowOptions(!showOptions)}
            >
              <Plus className="h-5 w-5" />
            </button>
            
            <input
              type="text"
              id="topic"
              className="block w-full py-3 bg-transparent border-none focus:ring-0 text-slate-900 dark:text-white placeholder-slate-400"
              placeholder="Ask anything..."
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  onSubmit?.();
                }
              }}
            />
            
            <div className="flex items-center gap-1 pl-2 pb-1">
              <button 
                type="button" 
                onClick={toggleListen}
                className={`p-2 rounded-full transition-colors flex items-center justify-center ${isListening ? 'bg-red-100 text-red-500 dark:bg-red-900/30' : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700'}`}
                aria-label="Voice input"
              >
                <Mic className={`h-5 w-5 ${isListening ? 'animate-pulse' : ''}`} />
              </button>
              <button 
                type="button" 
                className="p-2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-full transition-colors flex items-center justify-center"
                aria-label="Send"
                onClick={onSubmit}
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
