import type {
  Recommendation,
  LearningPathStep,
  PracticeQuestion,
  StudyEstimate,
  SkillProgress,
  RelatedTopic
} from '../types/recommendation';

// Delay helper to simulate network request
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

class RecommendationService {
  async getRecommendations(): Promise<Recommendation[]> {
    await delay(600);
    return [
      {
        id: 'rec_1',
        title: 'Linear Algebra Fundamentals',
        description: 'Understand the basic building blocks of matrices, vectors, and linear transformations.',
        difficulty: 'Intermediate',
        estimatedMinutes: 120,
        category: 'Mathematics',
        isPriority: true
      },
      {
        id: 'rec_2',
        title: 'Introduction to Neural Networks',
        description: 'Learn how artificial neurons learn patterns and optimize weights.',
        difficulty: 'Beginner',
        estimatedMinutes: 90,
        category: 'Machine Learning'
      },
      {
        id: 'rec_3',
        title: 'Advanced Prompt Engineering',
        description: 'Master zero-shot, few-shot, and chain-of-thought prompting techniques.',
        difficulty: 'Advanced',
        estimatedMinutes: 60,
        category: 'AI Application',
        isPriority: true
      }
    ];
  }

  async getLearningPath(): Promise<LearningPathStep[]> {
    await delay(500);
    return [
      { id: 'path_1', title: 'Introduction', description: 'Basic concepts and vocabulary', status: 'completed' },
      { id: 'path_2', title: 'Fundamentals', description: 'Core theories and foundations', status: 'completed' },
      { id: 'path_3', title: 'Practice', description: 'Apply concepts to real-world scenarios', status: 'current' },
      { id: 'path_4', title: 'Advanced Concepts', description: 'Deep dive into complex topics', status: 'locked' },
      { id: 'path_5', title: 'Assessment', description: 'Test your overall knowledge', status: 'locked' }
    ];
  }

  async getPracticeQuestions(): Promise<PracticeQuestion[]> {
    await delay(400);
    return [
      { id: 'q_1', question: 'Explain backpropagation in the context of neural networks.', difficulty: 'Intermediate', estimatedMinutes: 10 },
      { id: 'q_2', question: 'What is the difference between a zero-shot and a few-shot prompt?', difficulty: 'Beginner', estimatedMinutes: 5 },
      { id: 'q_3', question: 'Calculate the dot product of vectors [1, 2, 3] and [4, 5, 6].', difficulty: 'Beginner', estimatedMinutes: 3 }
    ];
  }

  async getRelatedTopics(): Promise<RelatedTopic[]> {
    await delay(300);
    return [
      { id: 'rt_1', title: 'Calculus', relevanceScore: 0.9 },
      { id: 'rt_2', title: 'Probability & Statistics', relevanceScore: 0.85 },
      { id: 'rt_3', title: 'Data Structures', relevanceScore: 0.6 }
    ];
  }

  async getSkillProgress(): Promise<SkillProgress[]> {
    await delay(300);
    return [
      { skill: 'Prompt Engineering', percentage: 80 },
      { skill: 'Problem Solving', percentage: 74 },
      { skill: 'Critical Thinking', percentage: 65 }
    ];
  }

  async getStudyEstimate(): Promise<StudyEstimate> {
    await delay(200);
    return {
      totalMinutes: 150, // 2h 30m
      dailyGoalMinutes: 45,
      completedMinutes: 20
    };
  }
}

export const recommendationService = new RecommendationService();
