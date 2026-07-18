import os
import json
import logging
from typing import List
from google import genai
from google.genai import types

from src.models.prompt_request import PromptRequest
from src.recommendations.schemas import RecommendationDashboard

logger = logging.getLogger("aithera.recommendations")

class RecommendationGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    async def generate_dashboard(self, prompt_history: List[PromptRequest]) -> RecommendationDashboard:
        """
        Generate a personalized recommendation dashboard based on the user's prompt history.
        """
        history_text = "No prior prompt history found. Provide general AI prompt engineering recommendations."
        if prompt_history:
            history_lines = []
            for idx, pr in enumerate(prompt_history[:10]):
                history_lines.append(f"{idx+1}. Topic: {pr.topic}, Style: {pr.learning_style}, Difficulty: {pr.difficulty}")
            history_text = "\n".join(history_lines)

        prompt = f"""
You are an AI learning assistant. Your goal is to analyze a user's recent prompt playground history and generate a personalized learning dashboard.

User's Recent Activity:
{history_text}

Based on this activity, generate a JSON object matching the following structure:
{{
  "recommendations": [
    {{ "id": "uuid", "title": "...", "description": "...", "difficulty": "Beginner|Intermediate|Advanced", "estimatedMinutes": 30, "category": "...", "isPriority": true }}
  ],
  "learningPath": [
    {{ "id": "uuid", "title": "...", "description": "...", "status": "completed|current|locked" }}
  ],
  "practiceQuestions": [
    {{ "id": "uuid", "question": "...", "difficulty": "Beginner|Intermediate|Advanced", "estimatedMinutes": 10 }}
  ],
  "relatedTopics": [
    {{ "id": "uuid", "title": "...", "relevanceScore": 0.95 }}
  ],
  "skillProgress": [
    {{ "skill": "...", "percentage": 85 }}
  ],
  "studyEstimate": {{
    "totalMinutes": 120,
    "dailyGoalMinutes": 60,
    "completedMinutes": 15
  }}
}}

Ensure that:
1. You provide at least 3 recommendations, 1 of which is Priority.
2. The learning path has exactly 5 steps (e.g. 2 completed, 1 current, 2 locked) representing their progression in prompt engineering or their current topics.
3. You provide at least 3 practice questions.
4. You provide 3-5 related topics.
5. You provide 3-5 skills with realistic percentages based on their history depth.
"""

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RecommendationDashboard,
                    temperature=0.7
                )
            )
            
            # response.text should now be a perfect JSON string matching the schema
            data = json.loads(response.text)
            return RecommendationDashboard.model_validate(data)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            raise e

recommendation_generator = RecommendationGenerator()
