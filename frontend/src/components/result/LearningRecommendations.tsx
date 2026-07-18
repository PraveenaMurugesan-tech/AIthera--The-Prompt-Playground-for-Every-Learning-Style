import React from 'react';
import { motion } from 'framer-motion';
import { Compass, ListChecks, Map } from 'lucide-react';

interface LearningRecommendationsProps {
  recommendations: {
    followUpTopics: string[];
    learningPath: string[];
    practiceSuggestions: string[];
  };
}

export const LearningRecommendations: React.FC<LearningRecommendationsProps> = ({ recommendations }) => {
  const sections = [
    {
      title: 'Learning Path',
      items: recommendations.learningPath,
      icon: Map,
      color: 'text-blue-500',
    },
    {
      title: 'Practice Suggestions',
      items: recommendations.practiceSuggestions,
      icon: ListChecks,
      color: 'text-emerald-500',
    },
    {
      title: 'Follow-Up Topics',
      items: recommendations.followUpTopics,
      icon: Compass,
      color: 'text-purple-500',
    }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {sections.map((section, idx) => {
        const Icon = section.icon;
        return (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + idx * 0.1 }}
            className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800"
          >
            <div className="flex items-center gap-2 mb-4">
              <Icon className={`w-5 h-5 ${section.color}`} />
              <h3 className="font-semibold text-slate-900 dark:text-white">
                {section.title}
              </h3>
            </div>
            <ul className="space-y-3">
              {section.items.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-slate-600 dark:text-slate-300">
                  <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600 mt-1.5"></span>
                  <span className="leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        );
      })}
    </div>
  );
};
