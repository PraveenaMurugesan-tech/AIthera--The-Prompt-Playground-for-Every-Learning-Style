import api from './api';
import type {
  Recommendation,
  LearningPathStep,
  PracticeQuestion,
  StudyEstimate,
  SkillProgress,
  RelatedTopic,
  TopicDetail
} from '../types/recommendation';

interface DashboardResponse {
  recommendations: Recommendation[];
  learningPath: LearningPathStep[];
  practiceQuestions: PracticeQuestion[];
  relatedTopics: RelatedTopic[];
  skillProgress: SkillProgress[];
  studyEstimate: StudyEstimate;
}

class RecommendationService {
  private dashboardData: DashboardResponse | null = null;
  private dashboardPromise: Promise<DashboardResponse> | null = null;

  invalidateCache() {
    this.dashboardData = null;
    this.dashboardPromise = null;
  }

  private async getDashboardData(): Promise<DashboardResponse> {
    if (this.dashboardData) {
      return this.dashboardData;
    }
    if (this.dashboardPromise) {
      return this.dashboardPromise;
    }
    
    this.dashboardPromise = api.get<DashboardResponse>('/recommendations/dashboard').then(res => {
      this.dashboardData = res.data;
      return res.data;
    }).finally(() => {
      this.dashboardPromise = null;
    });

    return this.dashboardPromise;
  }

  async getRecommendations(): Promise<Recommendation[]> {
    const data = await this.getDashboardData();
    return data.recommendations || [];
  }

  async getLearningPath(): Promise<LearningPathStep[]> {
    const data = await this.getDashboardData();
    return data.learningPath || [];
  }

  async getPracticeQuestions(): Promise<PracticeQuestion[]> {
    const data = await this.getDashboardData();
    return data.practiceQuestions || [];
  }

  async getRelatedTopics(): Promise<RelatedTopic[]> {
    const data = await this.getDashboardData();
    return data.relatedTopics || [];
  }

  async getSkillProgress(): Promise<SkillProgress[]> {
    const data = await this.getDashboardData();
    return data.skillProgress || [];
  }

  async getStudyEstimate(): Promise<StudyEstimate> {
    const data = await this.getDashboardData();
    return data.studyEstimate || {
      totalMinutes: 0,
      dailyGoalMinutes: 0,
      completedMinutes: 0
    };
  }

  async generateMorePracticeQuestions(): Promise<PracticeQuestion[]> {
    const response = await api.get<{ practiceQuestions: PracticeQuestion[] }>('/recommendations/practice-questions/generate');
    return response.data.practiceQuestions || [];
  }

  async getTopicDetail(topicName: string): Promise<TopicDetail> {
    const response = await api.get<TopicDetail>(`/recommendations/topic/${encodeURIComponent(topicName)}`);
    return response.data;
  }
}

export const recommendationService = new RecommendationService();

