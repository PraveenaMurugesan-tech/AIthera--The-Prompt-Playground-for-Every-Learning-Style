import { Compass, RefreshCw, Loader2 } from 'lucide-react';
import { useRecommendations } from '../../hooks/useRecommendations';
import { RecommendationCard } from '../../components/recommendations/RecommendationCard';
import { LearningPath } from '../../components/recommendations/LearningPath';
import { TopicCard } from '../../components/recommendations/TopicCard';
import { PracticeQuestions } from '../../components/recommendations/PracticeQuestions';
import { StudyTimeCard } from '../../components/recommendations/StudyTimeCard';
import { RelatedTopics } from '../../components/recommendations/RelatedTopics';
import { ProgressTracker } from '../../components/recommendations/ProgressTracker';
import { EmptyRecommendations } from '../../components/recommendations/EmptyRecommendations';
import { motion } from 'framer-motion';

export const RecommendationPage = () => {
  const {
    loading,
    error,
    recommendations,
    learningPath,
    practiceQuestions,
    relatedTopics,
    skillProgress,
    studyEstimate,
    refresh
  } = useRecommendations();

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-900">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
        <p className="text-slate-500 dark:text-slate-400 font-medium">
          Analyzing your learning profile...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-900 p-4 text-center">
        <p className="text-red-500 dark:text-red-400 mb-4">{error}</p>
        <button 
          onClick={refresh}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return <EmptyRecommendations />;
  }

  return (
    <div className="flex-1 overflow-auto bg-slate-50 dark:bg-slate-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl text-blue-600 dark:text-blue-400">
                <Compass className="w-8 h-8" />
              </div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">AI Recommendations</h1>
            </div>
            <p className="text-slate-500 dark:text-slate-400 text-lg max-w-2xl">
              Personalized learning path and topics based on your generated prompts.
            </p>
          </div>
          
          <button 
            onClick={refresh}
            className="self-start md:self-auto flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-700 transition-colors shadow-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Main Column */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            
            {/* Top Recommendations */}
            <section>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                Recommended For You
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.map((rec, index) => (
                  <motion.div
                    key={rec.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <RecommendationCard recommendation={rec} />
                  </motion.div>
                ))}
              </div>
            </section>

            {/* Quick Topics */}
            <section>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
                Explore Topics
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <TopicCard title="Zero-Shot Prompting" difficulty="Beginner" isRecommendedNext />
                <TopicCard title="Chain of Thought" difficulty="Intermediate" />
                <TopicCard title="Fine-Tuning Concepts" difficulty="Advanced" />
              </div>
            </section>

            {/* Practice Questions */}
            <section>
              <PracticeQuestions questions={practiceQuestions} />
            </section>

          </div>

          {/* Sidebar Column */}
          <div className="lg:col-span-4 flex flex-col gap-8">
            {studyEstimate && <StudyTimeCard estimate={studyEstimate} />}
            <LearningPath steps={learningPath} />
            <ProgressTracker skills={skillProgress} />
            <RelatedTopics topics={relatedTopics} />
          </div>

        </div>
      </div>
    </div>
  );
};
