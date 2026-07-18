export type Difficulty = 'Beginner' | 'Intermediate' | 'Advanced';

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  difficulty: Difficulty;
  estimatedMinutes: number;
  category: string;
  isPriority?: boolean;
}

export interface LearningPathStep {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'current' | 'locked';
}

export interface PracticeQuestion {
  id: string;
  question: string;
  difficulty: Difficulty;
  estimatedMinutes: number;
}

export interface StudyEstimate {
  totalMinutes: number;
  dailyGoalMinutes: number;
  completedMinutes: number;
}

export interface SkillProgress {
  skill: string;
  percentage: number;
}

export interface RelatedTopic {
  id: string;
  title: string;
  relevanceScore: number; // 0 to 1
}
