import React from 'react';
import { PromptForm } from '../../components/prompt/PromptForm';
import { CouncilStatusCard } from '../../components/prompt/CouncilStatusCard';
import { PromptTemplateCard } from '../../components/prompt/PromptTemplateCard';
import { SuggestedTopicsCard } from '../../components/prompt/SuggestedTopicsCard';
import { Sparkles } from 'lucide-react';

export const PromptPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-slate-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Page Header */}
        <header className="flex flex-col gap-2">
          <div className="flex items-center gap-3 text-[#2563EB] dark:text-blue-400">
            <Sparkles className="h-8 w-8" />
            <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
              Generate Learning Prompt
            </h1>
          </div>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl">
            Create personalized AI-powered educational prompts tailored to your learning style.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form Area */}
          <div className="lg:col-span-2 space-y-6">
            <PromptForm />
          </div>

          {/* Right Sidebar Area */}
          <div className="space-y-6">
            <CouncilStatusCard />
            <PromptTemplateCard />
            <SuggestedTopicsCard />
          </div>
        </div>
      </div>
    </div>
  );
};
