import { LightbulbOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const EmptyRecommendations = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
        <LightbulbOff className="w-10 h-10 text-slate-400" />
      </div>
      
      <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">
        No recommendations available yet
      </h2>
      
      <p className="text-slate-500 dark:text-slate-400 max-w-md mb-8">
        We need to understand your learning goals first. Generate a prompt or interact with the AI to receive personalized learning recommendations.
      </p>
      
      <button 
        onClick={() => navigate('/prompt')}
        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors shadow-sm"
      >
        Generate a Prompt
      </button>
    </div>
  );
};
