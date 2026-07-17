import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, AlertCircle } from 'lucide-react';
import { ProviderCard } from './ProviderCard';
import { CouncilProgress } from './CouncilProgress';
import { ConsensusAnimation } from './ConsensusAnimation';
import { promptService } from '../../services/promptService';
import type { ProviderState } from '../../services/promptService';

export const LoadingScreen: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const formData = useMemo(() => location.state?.formData || {}, [location.state?.formData]);
  const [providers, setProviders] = useState<ProviderState[]>(promptService.getInitialProviders());
  const [progress, setProgress] = useState(0);
  const [estimatedTime] = useState(15);
  
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    let interval: ReturnType<typeof setInterval>;

    const runGeneration = async () => {
      try {
        // Set all providers to processing to simulate council activity
        setProviders(prev => prev.map(p => ({ ...p, status: 'Processing' })));
        
        // Progress bar simulation while waiting for the synchronous backend call
        interval = setInterval(() => {
          setProgress(prev => Math.min(prev + 1, 95)); // Cap at 95% until done
        }, 600);

        // Await the real backend call
        const result = await promptService.generatePrompt(formData);
        
        clearInterval(interval);
        
        if (!isMounted) return;

        // Finish up animations
        setProgress(100);
        setProviders(prev => prev.map(p => ({ ...p, status: 'Completed' })));
        
        await new Promise(r => setTimeout(r, 800)); // Brief pause to show completion
        
        // Pass the result along with formData to the ResultPage
        navigate('/result', { state: { formData, resultData: result } });
      } catch (err: unknown) {
        clearInterval(interval);
        if (!isMounted) return;
        setProviders(prev => prev.map(p => ({ ...p, status: 'Failed' })));
        const errorMessage = err instanceof Error ? err.message : 'An error occurred during prompt generation.';
        setError(errorMessage);
      }
    };

    runGeneration();

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [navigate, formData]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8 flex items-center justify-center">
      <div className="max-w-4xl w-full bg-white dark:bg-slate-900 rounded-3xl shadow-xl border border-slate-200 dark:border-slate-800 p-8 md:p-12">
        <div className="flex flex-col md:flex-row gap-12">
          
          {/* Left side: Animation and Progress */}
          <div className="flex-1 space-y-12 flex flex-col justify-center">
            <div className="text-center space-y-4">
              <div className={`inline-flex items-center justify-center p-3 rounded-2xl mb-2 ${error ? 'bg-red-50 dark:bg-red-500/10' : 'bg-blue-50 dark:bg-blue-500/10'}`}>
                {error ? (
                  <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
                ) : (
                  <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                )}
              </div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">
                {error ? 'Generation Failed' : 'Generating Personalized Learning Prompt'}
              </h1>
              <p className={`text-slate-500 dark:text-slate-400 ${error ? 'text-red-500 dark:text-red-400' : ''}`}>
                {error ? error : 'Please wait while our AI Council evaluates and optimizes your request.'}
              </p>
              {error && (
                <button
                  onClick={() => navigate(-1)}
                  className="mt-6 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors duration-200 shadow-sm"
                >
                  Go Back and Try Again
                </button>
              )}
            </div>
            
            {!error && (
              <>
                <ConsensusAnimation progress={progress} />
                <CouncilProgress progress={progress} estimatedTime={estimatedTime} />
              </>
            )}
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

