import { useState } from 'react';
import { Network, ArrowRight, X, Loader2, PlayCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { RelatedTopic, TopicDetail } from '../../types/recommendation';
import { recommendationService } from '../../services/recommendationService';

interface RelatedTopicsProps {
  topics: RelatedTopic[];
}

export const RelatedTopics = ({ topics }: RelatedTopicsProps) => {
  const [selectedTopic, setSelectedTopic] = useState<TopicDetail | null>(null);
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleTopicClick = async (topicTitle: string) => {
    setIsLoading(topicTitle);
    try {
      const detail = await recommendationService.getTopicDetail(topicTitle);
      setSelectedTopic(detail);
    } catch (error) {
      console.error("Failed to load topic details", error);
    } finally {
      setIsLoading(null);
    }
  };

  const handlePromptClick = (promptStr: string) => {
    navigate('/prompt', { state: { topic: promptStr } });
  };

  return (
    <>
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-5">
          <Network className="w-5 h-5 text-emerald-500" />
          <h3 className="font-bold text-lg text-slate-900 dark:text-white">Related Concepts</h3>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {topics.map((topic) => (
            <button 
              key={topic.id}
              onClick={() => handleTopicClick(topic.title)}
              disabled={isLoading === topic.title}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 hover:bg-emerald-50 dark:bg-slate-900/50 dark:hover:bg-emerald-900/20 text-slate-700 dark:text-slate-300 hover:text-emerald-700 dark:hover:text-emerald-400 border border-slate-200 dark:border-slate-700 hover:border-emerald-200 dark:hover:border-emerald-800/50 rounded-lg text-sm font-medium transition-colors group disabled:opacity-50"
            >
              {isLoading === topic.title ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <>
                  {topic.title}
                  <ArrowRight className="w-3.5 h-3.5 opacity-50 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all" />
                </>
              )}
            </button>
          ))}
        </div>
      </div>

      {selectedTopic && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-slate-900 rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 dark:border-slate-800">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{selectedTopic.topic}</h2>
                <button onClick={() => setSelectedTopic(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <p className="text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
                {selectedTopic.description}
              </p>

              <h4 className="font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <PlayCircle className="w-5 h-5 text-emerald-500" />
                Suggested Prompts
              </h4>
              <div className="space-y-3">
                {selectedTopic.suggestedPrompts.map((promptStr, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptClick(promptStr)}
                    className="w-full text-left p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-emerald-500 dark:hover:border-emerald-500 hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors text-sm text-slate-700 dark:text-slate-300"
                  >
                    {promptStr}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
