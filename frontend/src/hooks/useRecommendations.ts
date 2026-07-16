import { useState, useEffect, useCallback } from 'react';
import { recommendationService } from '../services/recommendationService';
import type {
  Recommendation,
  LearningPathStep,
  PracticeQuestion,
  StudyEstimate,
  SkillProgress,
  RelatedTopic
} from '../types/recommendation';

export function useRecommendations() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [learningPath, setLearningPath] = useState<LearningPathStep[]>([]);
  const [practiceQuestions, setPracticeQuestions] = useState<PracticeQuestion[]>([]);
  const [relatedTopics, setRelatedTopics] = useState<RelatedTopic[]>([]);
  const [skillProgress, setSkillProgress] = useState<SkillProgress[]>([]);
  const [studyEstimate, setStudyEstimate] = useState<StudyEstimate | null>(null);

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch all data concurrently
      const [
        recs,
        path,
        questions,
        topics,
        skills,
        estimate
      ] = await Promise.all([
        recommendationService.getRecommendations(),
        recommendationService.getLearningPath(),
        recommendationService.getPracticeQuestions(),
        recommendationService.getRelatedTopics(),
        recommendationService.getSkillProgress(),
        recommendationService.getStudyEstimate()
      ]);

      setRecommendations(recs);
      setLearningPath(path);
      setPracticeQuestions(questions);
      setRelatedTopics(topics);
      setSkillProgress(skills);
      setStudyEstimate(estimate);
    } catch (err: any) {
      console.error('Failed to fetch recommendations:', err);
      setError(err.message || 'An error occurred while fetching recommendations.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  return {
    loading,
    error,
    recommendations,
    learningPath,
    practiceQuestions,
    relatedTopics,
    skillProgress,
    studyEstimate,
    refresh: fetchAllData
  };
}
