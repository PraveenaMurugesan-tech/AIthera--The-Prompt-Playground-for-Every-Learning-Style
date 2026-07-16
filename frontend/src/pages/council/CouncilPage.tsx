import React, { useState, useEffect } from 'react';
import { ShieldAlert, Network } from 'lucide-react';
import { ProviderGrid } from '../../components/ai/ProviderGrid';
import { ConsensusMeter } from '../../components/ai/ConsensusMeter';
import { CouncilTimeline } from '../../components/ai/CouncilTimeline';
import { AgreementChart } from '../../components/ai/AgreementChart';
import type { ExtendedProviderState } from '../../components/ai/ProviderStatusCard';

export const CouncilPage: React.FC = () => {
  const [providers, setProviders] = useState<ExtendedProviderState[]>([
    { id: 'claude', name: 'Claude', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'gemini', name: 'Gemini', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'deepseek', name: 'DeepSeek', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'groq', name: 'Groq', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'cerebras', name: 'Cerebras', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'sambanova', name: 'SambaNova', status: 'Waiting', confidence: 0, responseTime: 0 },
    { id: 'openrouter', name: 'OpenRouter', status: 'Waiting', confidence: 0, responseTime: 0 },
  ]);

  const [timelineSteps, setTimelineSteps] = useState([
    { id: '1', label: 'Generating', active: true, completed: false },
    { id: '2', label: 'Provider Responses', active: false, completed: false },
    { id: '3', label: 'Normalization', active: false, completed: false },
    { id: '4', label: 'Consensus', active: false, completed: false },
    { id: '5', label: 'Final Prompt', active: false, completed: false },
  ]);

  useEffect(() => {
    // Simulation Logic
    const runSimulation = async () => {
      // Step 1: Processing
      await new Promise(r => setTimeout(r, 1000));
      setProviders(prev => prev.map(p => ({ ...p, status: 'Processing' })));
      setTimelineSteps(prev => prev.map(s => s.id === '1' ? { ...s, completed: true, active: false } : s.id === '2' ? { ...s, active: true } : s));

      // Step 2: Responses complete
      await new Promise(r => setTimeout(r, 2000));
      setProviders(prev => prev.map(p => ({ 
        ...p, 
        status: 'Completed', 
        confidence: Math.floor(Math.random() * 15) + 80, // 80-95
        responseTime: Math.floor(Math.random() * 800) + 200 // 200-1000ms
      })));
      setTimelineSteps(prev => prev.map(s => s.id === '2' ? { ...s, completed: true, active: false } : s.id === '3' ? { ...s, active: true } : s));

      // Step 3: Normalization
      await new Promise(r => setTimeout(r, 1500));
      setTimelineSteps(prev => prev.map(s => s.id === '3' ? { ...s, completed: true, active: false } : s.id === '4' ? { ...s, active: true } : s));

      // Step 4: Consensus
      await new Promise(r => setTimeout(r, 1500));
      setTimelineSteps(prev => prev.map(s => s.id === '4' ? { ...s, completed: true, active: false } : s.id === '5' ? { ...s, active: true } : s));

      // Step 5: Final
      await new Promise(r => setTimeout(r, 1000));
      setTimelineSteps(prev => prev.map(s => s.id === '5' ? { ...s, completed: true, active: false } : s));
    };

    runSimulation();
  }, []);

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex flex-col gap-2">
          <div className="flex items-center gap-3 text-indigo-600 dark:text-indigo-500">
            <Network className="h-8 w-8" />
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
              AI Council Visualization
            </h1>
          </div>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl">
            Watch the multi-model consensus algorithm in real-time.
          </p>
        </header>

        {/* Timeline */}
        <div className="bg-white dark:bg-slate-900 p-8 rounded-2xl border border-slate-200 dark:border-slate-800">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-8">Generation Lifecycle</h2>
          <div className="px-4">
            <CouncilTimeline steps={timelineSteps} />
          </div>
        </div>

        {/* Providers */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Provider Status</h2>
          <ProviderGrid providers={providers} />
        </div>

        {/* Consensus Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 flex justify-around items-center">
             <ConsensusMeter score={91} label="Agreement Score" color="text-blue-500" strokeColor="text-blue-500" />
             <ConsensusMeter score={94} label="Confidence Score" color="text-emerald-500" strokeColor="text-emerald-500" />
          </div>
          
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
             <AgreementChart />
          </div>

          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
             <div className="flex items-center gap-2 mb-4 text-indigo-600 dark:text-indigo-400">
               <ShieldAlert className="w-6 h-6" />
               <h3 className="font-semibold text-lg text-slate-900 dark:text-white">Quality Metrics</h3>
             </div>
             <div className="space-y-4">
                <div className="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-600 dark:text-slate-400">Average Response Time</span>
                  <span className="font-mono font-medium text-slate-900 dark:text-white">650ms</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-800">
                  <span className="text-slate-600 dark:text-slate-400">Prompt Quality</span>
                  <span className="font-medium text-emerald-500">Excellent</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-600 dark:text-slate-400">Models Consulted</span>
                  <span className="font-mono font-medium text-slate-900 dark:text-white">7/7</span>
                </div>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
};
