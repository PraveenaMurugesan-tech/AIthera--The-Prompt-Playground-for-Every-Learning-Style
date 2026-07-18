import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Sparkles, RefreshCw } from 'lucide-react';
import { OptimizedPromptCard } from '../../components/result/OptimizedPromptCard';
import { ConsensusSummary } from '../../components/result/ConsensusSummary';
import { ScoreCards } from '../../components/result/ScoreCards';
import { EducationalMetrics } from '../../components/result/EducationalMetrics';
import { LearningRecommendations } from '../../components/result/LearningRecommendations';
import { PromptVariants } from '../../components/result/PromptVariants';
import { ConfirmDialog } from '../../components/common/ConfirmDialog';
import type { GenerationResult } from '../../services/promptService';

export const ResultPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const [result] = useState<GenerationResult | null>(location.state?.resultData || null);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    // If someone navigated directly here without state, redirect to prompt page
    if (!result) {
      navigate('/prompt');
    }
  }, [result, navigate]);

  if (!result) {
    return null;
  }

  const handleRegenerate = () => {
    setShowConfirm(false);
    navigate('/prompt');
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/prompt')}
              className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors text-slate-500 dark:text-slate-400"
              aria-label="Go back to prompt generator"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-500">
              <Sparkles className="w-6 h-6" />
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                AI Generation Results
              </h1>
            </div>
          </div>
          <button
            onClick={() => setShowConfirm(true)}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-sm self-start md:self-auto flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Regenerate Prompt
          </button>
        </header>

        {/* Main Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column (Primary Content) */}
          <div className="lg:col-span-2 space-y-8">
            <OptimizedPromptCard prompt={result.optimizedPrompt} />
            <PromptVariants variants={result.variants} />
          </div>

          {/* Right Column (Meta & Scores) */}
          <div className="space-y-6">
            <ScoreCards confidence={result.confidenceScore} agreement={result.agreementScore} />
            <ConsensusSummary summary={result.consensusSummary} />
          </div>
        </div>

        {/* Full Width Sections */}
        <div className="space-y-6 pt-4 border-t border-slate-200 dark:border-slate-800">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Educational Profile
          </h2>
          <EducationalMetrics metrics={result.educationalMetrics} />
        </div>

        <div className="space-y-6 pt-4 border-t border-slate-200 dark:border-slate-800">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            Next Steps & Recommendations
          </h2>
          <LearningRecommendations recommendations={result.recommendations} />
        </div>

      </div>

      <ConfirmDialog
        isOpen={showConfirm}
        title="Regenerate Prompt"
        message="Are you sure you want to discard this prompt and generate a new one? Your current results will be lost unless saved to history."
        confirmLabel="Regenerate"
        cancelLabel="Cancel"
        onConfirm={handleRegenerate}
        onCancel={() => setShowConfirm(false)}
      />
    </div>
  );
};
