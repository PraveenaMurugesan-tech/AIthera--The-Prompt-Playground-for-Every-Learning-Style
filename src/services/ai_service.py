import logging
from typing import Dict, Any, List, Optional
import asyncio

from src.models.prompt_request import PromptRequest
from src.council.live_council import LiveCouncil
from src.optimizer.prompt_optimizer import PromptOptimizer
from src.optimizer.difficulty_adapter import DifficultyAdapter, DifficultyLevel
from src.optimizer.bloom_engine import BloomEngine, BloomLevel
from src.optimizer.prompt_variants import PromptVariantsGenerator, PromptVariant, VariantStyle
from src.optimizer.learning_path import LearningPathGenerator, LearningPath
from src.optimizer.prompt_validator import PromptValidator, ValidationScore
from src.optimizer.recommendation_engine import RecommendationEngine, Recommendation

logger = logging.getLogger("aithera.ai_service")

class AIServiceError(Exception):
    pass

class AIService:
    """
    High-level service integrating the AI Council and the Prompt Intelligence Engine.
    Exposes clean interfaces for all AI-driven prompt operations.
    """

    def __init__(
        self,
        live_council: Optional[LiveCouncil] = None,
        prompt_optimizer: Optional[PromptOptimizer] = None,
        difficulty_adapter: Optional[DifficultyAdapter] = None,
        bloom_engine: Optional[BloomEngine] = None,
        variants_generator: Optional[PromptVariantsGenerator] = None,
        learning_path_gen: Optional[LearningPathGenerator] = None,
        prompt_validator: Optional[PromptValidator] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ):
        self.live_council = live_council or LiveCouncil()
        self.prompt_optimizer = prompt_optimizer or PromptOptimizer()
        self.difficulty_adapter = difficulty_adapter or DifficultyAdapter()
        self.bloom_engine = bloom_engine or BloomEngine()
        self.variants_generator = variants_generator or PromptVariantsGenerator()
        self.learning_path_gen = learning_path_gen or LearningPathGenerator()
        self.prompt_validator = prompt_validator or PromptValidator()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    async def generate_prompt(self, request: PromptRequest, timeout: float = 300.0) -> Dict[str, Any]:
        """
        Executes the full Live Council to generate and build consensus on a prompt.
        """
        try:
            return await self.live_council.execute(request, timeout=timeout)
        except Exception as e:
            logger.error(f"Error in generate_prompt: {e}")
            raise AIServiceError(f"Failed to generate prompt: {e}")

    def optimize_prompt(self, prompt: str) -> str:
        """
        Optimizes a prompt by removing redundancy and improving readability.
        """
        return self.prompt_optimizer.optimize(prompt)

    async def generate_learning_path(self, topic: str, difficulty: str = "beginner") -> Optional[LearningPath]:
        """
        Generates a structured learning path using the AI Council.
        """
        # Create a mock request to pass through the council
        request = PromptRequest(
            topic=topic,
            learning_style="step_by_step",
            difficulty=difficulty,
            education_level=difficulty,
            output_length="long",
            objective="Generate a structured learning path."
        )
        
        # Override the template/objective temporarily by injecting the specific path generation prompt
        # In a real implementation, we'd have a specific Council flow for JSON data generation.
        # For this integration, we'll use the prompt generator string as the objective.
        path_prompt = self.learning_path_gen.generate_path_prompt(topic, difficulty)
        request.objective = path_prompt
        
        try:
            result = await self.live_council.execute(request)
            consensus_text = result["consensus"].final_prompt
            return self.learning_path_gen.parse_path_response(consensus_text)
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return None

    def generate_prompt_variants(self, base_topic: str, styles: Optional[List[VariantStyle]] = None) -> List[PromptVariant]:
        """
        Generates different stylistic variations for a given topic.
        """
        return self.variants_generator.generate_variants(base_topic, styles)

    def validate_prompt(self, prompt: str) -> ValidationScore:
        """
        Scores a prompt based on educational criteria.
        """
        return self.prompt_validator.validate(prompt)

    def generate_recommendations(
        self,
        prompt: str,
        learning_style: str,
        difficulty: str,
        validation_score: Optional[ValidationScore] = None
    ) -> List[Recommendation]:
        """
        Generates actionable recommendations to improve a prompt.
        """
        if not validation_score:
            validation_score = self.validate_prompt(prompt)
            
        return self.recommendation_engine.generate_recommendations(
            prompt, learning_style, difficulty, validation_score
        )

    def adapt_difficulty(self, prompt: str, target_level: DifficultyLevel | str) -> str:
        """
        Adapts an existing prompt to a specific difficulty level constraints.
        """
        return self.difficulty_adapter.adapt(prompt, target_level)

    def generate_bloom_prompt(self, base_topic: str, level: BloomLevel | str) -> str:
        """
        Generates a prompt template targeted at a specific Bloom's Taxonomy level.
        """
        return self.bloom_engine.generate_prompt(base_topic, level)
