import { HelpCircle, Clock, Loader2 } from 'lucide-react';
import type { PracticeQuestion } from '../../types/recommendation';
import { DifficultyBadge } from './DifficultyBadge';

interface PracticeQuestionsProps {
  questions: PracticeQuestion[];
  onGenerateMore: () => void;
  isGeneratingQuestions: boolean;
  onQuestionClick: (question: PracticeQuestion) => void;
}

export const PracticeQuestions = ({ 
  questions, 
  onGenerateMore, 
  isGeneratingQuestions, 
  onQuestionClick 
}: PracticeQuestionsProps) => {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6">
        <HelpCircle className="w-5 h-5 text-indigo-500" />
        <h3 className="font-bold text-lg text-slate-900 dark:text-white">Practice Questions</h3>
      </div>
      
      <div className="space-y-4">
        {questions.map((q, index) => (
          <div 
            key={q.id} 
            onClick={() => onQuestionClick(q)}
            className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700/50 hover:border-indigo-200 dark:hover:border-indigo-800 transition-colors cursor-pointer group"
          >
            <div className="flex justify-between items-start mb-3 gap-4">
              <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5">
                Q{index + 1}
              </span>
              <p className="text-sm font-medium text-slate-900 dark:text-slate-100 flex-1 leading-snug">
                {q.question}
              </p>
            </div>
            
            <div className="flex items-center justify-between ml-8">
              <DifficultyBadge difficulty={q.difficulty} />
              <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                <Clock className="w-3.5 h-3.5" />
                <span>{q.estimatedMinutes}m</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <button 
        onClick={onGenerateMore}
        disabled={isGeneratingQuestions}
        className="w-full mt-6 py-2.5 flex justify-center items-center gap-2 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-900/20 dark:hover:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400 rounded-xl text-sm font-semibold transition-colors border border-indigo-100 dark:border-indigo-800/50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isGeneratingQuestions ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Generating...
          </>
        ) : (
          'Generate More Questions'
        )}
      </button>
    </div>
  );
};
