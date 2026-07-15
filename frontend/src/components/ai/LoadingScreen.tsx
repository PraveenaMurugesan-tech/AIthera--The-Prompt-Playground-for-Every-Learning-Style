import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { ProviderCard } from './ProviderCard';
import { CouncilProgress } from './CouncilProgress';
import { ConsensusAnimation } from './ConsensusAnimation';
import { promptService } from '../../services/promptService';
import type { ProviderState } from '../../services/promptService';

export const LoadingScreen: React.FC = () => {
  const navigate = useNavigate();
  const [providers, setProviders] = useState<ProviderState[]>(promptService.getInitialProviders());
  const [progress, setProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(15);
  
  useEffect(() => {
    // Simulate the generation process
    let currentProgress = 0;
    
    // Simulate provider state changes
    const runSimulation = async () => {
      // Small initial delay
      await new Promise(r => setTimeout(r, 500));
      
      const updateProvider = (index: number, status: ProviderState['status']) => {
        setProviders(prev => {
          const newProviders = [...prev];
          newProviders[index] = { ...newProviders[index], status };
          return newProviders;
        });
      };

      // 1. GPT & Claude start processing
      updateProvider(0, 'Processing');
      updateProvider(1, 'Processing');
      
      await new Promise(r => setTimeout(r, 2000));
      updateProvider(0, 'Completed');
      updateProvider(2, 'Processing');
      
      await new Promise(r => setTimeout(r, 1500));
      updateProvider(1, 'Completed');
      updateProvider(3, 'Processing');
      updateProvider(4, 'Processing');
      
      await new Promise(r => setTimeout(r, 2500));
      updateProvider(2, 'Completed');
      updateProvider(3, 'Completed');
      updateProvider(5, 'Processing');
      updateProvider(6, 'Processing');
      
      await new Promise(r => setTimeout(r, 2000));
      updateProvider(4, 'Completed');
      updateProvider(7, 'Processing');
      
      await new Promise(r => setTimeout(r, 1500));
      updateProvider(5, 'Completed');
      updateProvider(6, 'Completed');
      updateProvider(7, 'Completed');
      
      // All completed, wait a moment then navigate
      await new Promise(r => setTimeout(r, 1000));
      navigate('/result');
    };

    runSimulation();

    // Progress bar and timer simulation
    const interval = setInterval(() => {
      currentProgress += 1; // Increase by 1% roughly every 100ms -> 10 seconds total
      setProgress(Math.min(currentProgress, 100));
      
      if (currentProgress % 10 === 0) {
        setEstimatedTime(prev => Math.max(0, prev - 1));
      }

      if (currentProgress >= 100) {
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8 flex items-center justify-center">
      <div className="max-w-4xl w-full bg-white dark:bg-slate-900 rounded-3xl shadow-xl border border-slate-200 dark:border-slate-800 p-8 md:p-12">
        <div className="flex flex-col md:flex-row gap-12">
          
          {/* Left side: Animation and Progress */}
          <div className="flex-1 space-y-12 flex flex-col justify-center">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center p-3 bg-blue-50 dark:bg-blue-500/10 rounded-2xl mb-2">
                <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">
                Generating Personalized Learning Prompt
              </h1>
              <p className="text-slate-500 dark:text-slate-400">
                Please wait while our AI Council evaluates and optimizes your request.
              </p>
            </div>
            
            <ConsensusAnimation progress={progress} />
            <CouncilProgress progress={progress} estimatedTime={estimatedTime} />
          </div>
          
          {/* Right side: Provider Status Grid */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-6">
              Council Status
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {providers.map((provider) => (
                <ProviderCard key={provider.id} provider={provider} />
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};
