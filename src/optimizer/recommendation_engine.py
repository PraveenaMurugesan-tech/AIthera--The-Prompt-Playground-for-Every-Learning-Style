import logging
from typing import List
from pydantic import BaseModel, Field

from .prompt_validator import ValidationScore

logger = logging.getLogger("aithera.recommendation_engine")

class Recommendation(BaseModel):
    category: str = Field(..., description="Category of the recommendation (e.g., 'Visuals', 'Exercises')")
    suggestion: str = Field(..., description="The actionable suggestion")
    reasoning: str = Field(..., description="Why this suggestion improves the prompt")

class RecommendationEngine:
    """Generates actionable recommendations to improve educational prompts."""
    
    def __init__(self):
        pass

    def generate_recommendations(
        self, 
        prompt: str, 
        learning_style: str, 
        difficulty: str, 
        validation_score: ValidationScore
    ) -> List[Recommendation]:
        """
        Generates targeted recommendations based on prompt characteristics and scores.
        
        Args:
            prompt: The original prompt.
            learning_style: The target learning style.
            difficulty: The target difficulty level.
            validation_score: The validation scores for the prompt.
            
        Returns:
            A list of Recommendation objects.
        """
        recommendations = []
        lower_prompt = prompt.lower()

        # 1. Learning Style Recommendations
        style_norm = learning_style.lower()
        if "visual" in style_norm and "diagram" not in lower_prompt and "chart" not in lower_prompt and "image" not in lower_prompt:
            recommendations.append(Recommendation(
                category="Visual Aids",
                suggestion="Request the inclusion of ASCII diagrams, charts, or visual analogies.",
                reasoning="Visual learners benefit significantly from spatial representations of data or concepts."
            ))
        elif "step" in style_norm and "step-by-step" not in lower_prompt and "process" not in lower_prompt:
            recommendations.append(Recommendation(
                category="Structure",
                suggestion="Explicitly request a numbered, step-by-step breakdown.",
                reasoning="Step-by-step learners need clear, sequential instructions without cognitive leaps."
            ))
        elif "conversational" in style_norm and "dialogue" not in lower_prompt and "chat" not in lower_prompt:
             recommendations.append(Recommendation(
                category="Format",
                suggestion="Frame the prompt as a Socratic dialogue or interview.",
                reasoning="Conversational learners engage better with interactive, back-and-forth formats."
            ))

        # 2. Difficulty Recommendations
        diff_norm = difficulty.lower()
        if diff_norm == "beginner" and "simple" not in lower_prompt and "analogy" not in lower_prompt:
            recommendations.append(Recommendation(
                category="Complexity",
                suggestion="Ask the AI to use everyday analogies and avoid technical jargon.",
                reasoning="Beginners need familiar anchors to understand new, abstract concepts."
            ))
        elif diff_norm in ["advanced", "expert"] and "edge cases" not in lower_prompt and "trade-offs" not in lower_prompt:
            recommendations.append(Recommendation(
                category="Depth",
                suggestion="Request analysis of edge cases, performance trade-offs, and architectural limitations.",
                reasoning="Advanced learners need to understand the boundaries and weaknesses of concepts, not just the happy path."
            ))

        # 3. Validation Score Recommendations
        if validation_score.clarity_score < 7.0:
            recommendations.append(Recommendation(
                category="Clarity",
                suggestion="Specify exactly what role the AI should play (e.g., 'Act as a Senior Python Developer').",
                reasoning="Role-prompting drastically improves the clarity and focus of the AI's output."
            ))
            
        if validation_score.educational_value_score < 8.0:
            recommendations.append(Recommendation(
                category="Exercises",
                suggestion="Ask the AI to generate a mini-project or practice exercise at the end.",
                reasoning="Active recall and application solidify learning much better than passive reading."
            ))

        if "example" not in lower_prompt:
            recommendations.append(Recommendation(
                category="Examples",
                suggestion="Explicitly request at least two contrasting examples.",
                reasoning="Contrasting examples help learners identify the defining features of a concept."
            ))

        return recommendations
