from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    id: str
    title: str
    description: str
    difficulty: Literal['Beginner', 'Intermediate', 'Advanced']
    estimatedMinutes: int
    category: str
    isPriority: Optional[bool] = False

class LearningPathStep(BaseModel):
    id: str
    title: str
    description: str
    status: Literal['completed', 'current', 'locked']

class PracticeQuestion(BaseModel):
    id: str
    question: str
    difficulty: Literal['Beginner', 'Intermediate', 'Advanced']
    estimatedMinutes: int

class StudyEstimate(BaseModel):
    totalMinutes: int
    dailyGoalMinutes: int
    completedMinutes: int

class SkillProgress(BaseModel):
    skill: str
    percentage: int

class RelatedTopic(BaseModel):
    id: str
    title: str
    relevanceScore: float

class RecommendationDashboard(BaseModel):
    recommendations: List[Recommendation]
    learningPath: List[LearningPathStep]
    practiceQuestions: List[PracticeQuestion]
    relatedTopics: List[RelatedTopic]
    skillProgress: List[SkillProgress]
    studyEstimate: StudyEstimate

class PracticeQuestionsResponse(BaseModel):
    practiceQuestions: List[PracticeQuestion]

class TopicDetail(BaseModel):
    topic: str
    description: str
    suggestedPrompts: List[str]
