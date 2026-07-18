import { motion } from 'framer-motion';
import { VoiceRecorder } from '../../components/voice/VoiceRecorder';
import { VoicePlayer } from '../../components/voice/VoicePlayer';
import { Mic2 } from 'lucide-react';

export const VoicePage = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-6xl mx-auto space-y-8 p-6"
    >
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl text-blue-600 dark:text-blue-400">
            <Mic2 className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold">Voice Learning (Updated)</h1>
        </div>
        <p className="text-slate-500 dark:text-slate-400 text-lg max-w-2xl">
          Interact with AIthera using your voice. Record prompts using speech recognition, 
          or have AI responses read aloud with customizable text-to-speech settings.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <section className="bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 p-6 rounded-2xl shadow-sm">
          <VoiceRecorder />
        </section>

        <section className="bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 p-6 rounded-2xl shadow-sm">
          <VoicePlayer />
        </section>
      </div>
    </motion.div>
  );
};
