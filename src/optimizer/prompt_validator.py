import logging
from typing import Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("aithera.prompt_validator")

class ValidationScore(BaseModel):
    clarity_score: float = Field(..., description="Score for clarity (0-10)")
    completeness_score: float = Field(..., description="Score for completeness (0-10)")
    readability_score: float = Field(..., description="Score for readability (0-10)")
    educational_value_score: float = Field(..., description="Score for educational value (0-10)")
    overall_score: float = Field(..., description="Aggregate score (0-100)")
    feedback: str = Field(..., description="Specific feedback on the prompt")

class PromptValidator:
    """Validates and scores prompts based on educational criteria."""
    
    def __init__(self):
        # Weightings for overall score calculation
        self.weights = {
            "clarity": 0.3,
            "completeness": 0.2,
            "readability": 0.2,
            "educational_value": 0.3
        }

    def _calculate_clarity(self, prompt: str) -> float:
        """Heuristic for clarity (simulated)."""
        # In a real system, this might use an LLM or specific NLP metrics.
        # Here we use a simple length and structure heuristic.
        score = 10.0
        if len(prompt) < 20:
            score -= 4.0
        if "what" not in prompt.lower() and "how" not in prompt.lower() and "explain" not in prompt.lower():
            score -= 2.0
        return max(0.0, score)

    def _calculate_completeness(self, prompt: str) -> float:
        """Heuristic for completeness."""
        score = 10.0
        if len(prompt.split()) < 10:
            score -= 5.0
        return max(0.0, score)

    def _calculate_readability(self, prompt: str) -> float:
        """Heuristic for readability."""
        score = 10.0
        # Check for paragraph breaks or lists
        if "\n" not in prompt and len(prompt) > 200:
            score -= 3.0
        # Very long sentences
        sentences = [s for s in prompt.split('.') if s.strip()]
        for s in sentences:
            if len(s.split()) > 30:
                score -= 1.0
        return max(0.0, score)

    def _calculate_educational_value(self, prompt: str) -> float:
        """Heuristic for educational value."""
        score = 5.0 # Base score
        educational_keywords = ["learn", "understand", "example", "exercise", "practice", "why", "how", "concept"]
        for kw in educational_keywords:
            if kw in prompt.lower():
                score += 1.0
        return min(10.0, score)

    def validate(self, prompt: str) -> ValidationScore:
        """
        Scores a prompt across multiple dimensions.
        
        Args:
            prompt: The prompt to validate.
            
        Returns:
            A ValidationScore object containing metrics and feedback.
        """
        if not prompt or not prompt.strip():
            return ValidationScore(
                clarity_score=0.0,
                completeness_score=0.0,
                readability_score=0.0,
                educational_value_score=0.0,
                overall_score=0.0,
                feedback="Prompt is empty."
            )

        clarity = self._calculate_clarity(prompt)
        completeness = self._calculate_completeness(prompt)
        readability = self._calculate_readability(prompt)
        edu_value = self._calculate_educational_value(prompt)

        # Calculate weighted average and scale to 0-100
        overall = (
            (clarity * self.weights["clarity"]) +
            (completeness * self.weights["completeness"]) +
            (readability * self.weights["readability"]) +
            (edu_value * self.weights["educational_value"])
        ) * 10.0

        feedback = []
        if clarity < 7.0:
            feedback.append("Prompt could be more clear. Add 'how' or 'explain' directives.")
        if completeness < 7.0:
            feedback.append("Prompt is too brief to be considered complete.")
        if readability < 7.0:
            feedback.append("Consider breaking the prompt into smaller paragraphs or bullet points.")
        if edu_value < 7.0:
            feedback.append("Add educational keywords like 'example' or 'practice' to increase value.")
            
        if not feedback:
            feedback.append("Prompt looks solid across all metrics.")

        return ValidationScore(
            clarity_score=clarity,
            completeness_score=completeness,
            readability_score=readability,
            educational_value_score=edu_value,
            overall_score=round(overall, 2),
            feedback=" ".join(feedback)
        )
