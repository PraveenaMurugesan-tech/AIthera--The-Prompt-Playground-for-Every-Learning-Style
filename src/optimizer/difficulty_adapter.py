import logging
from enum import Enum
from typing import Dict

logger = logging.getLogger("aithera.difficulty_adapter")

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class DifficultyAdapter:
    """Adapts prompts to different difficulty levels."""
    
    def __init__(self):
        self.level_profiles = {
            DifficultyLevel.BEGINNER: {
                "vocabulary": "Use simple, accessible language. Avoid jargon or define it immediately in plain terms.",
                "explanation_depth": "Focus on the 'what' and 'why' at a high level. Use analogies related to everyday life.",
                "challenge_level": "Provide step-by-step guidance. Do not assume prior knowledge.",
                "examples": "Use simple, concrete examples that clearly illustrate the core concept.",
                "exercises": "Provide straightforward, guided exercises with clear right/wrong answers.",
            },
            DifficultyLevel.INTERMEDIATE: {
                "vocabulary": "Use standard domain terminology. Introduce some advanced concepts but provide context.",
                "explanation_depth": "Explain the mechanics and standard practices. Connect concepts together.",
                "challenge_level": "Require some independent problem solving, but provide hints or frameworks.",
                "examples": "Use realistic, practical examples showing standard use cases.",
                "exercises": "Provide exercises that require combining multiple concepts.",
            },
            DifficultyLevel.ADVANCED: {
                "vocabulary": "Use precise, technical domain terminology. Assume familiarity with standard concepts.",
                "explanation_depth": "Focus on edge cases, performance, architecture, and underlying principles.",
                "challenge_level": "Present complex, open-ended problems requiring critical thinking.",
                "examples": "Use complex, nuanced examples highlighting trade-offs.",
                "exercises": "Provide challenging exercises requiring optimization or debugging of complex systems.",
            },
            DifficultyLevel.EXPERT: {
                "vocabulary": "Use advanced academic or industry-standard terminology without hesitation.",
                "explanation_depth": "Discuss theoretical limits, novel applications, and paradigm-shifting implications.",
                "challenge_level": "Present cutting-edge or unsolved problems. Require deep architectural synthesis.",
                "examples": "Use highly specialized or abstract examples.",
                "exercises": "Provide research-oriented or highly complex design tasks without obvious solutions.",
            }
        }

    def adapt(self, prompt: str, target_level: DifficultyLevel | str) -> str:
        """
        Adapts a base prompt for a specific difficulty level.
        
        Args:
            prompt: The original prompt.
            target_level: The target difficulty level.
            
        Returns:
            An adapted prompt incorporating difficulty constraints.
        """
        try:
            level = DifficultyLevel(target_level.lower() if isinstance(target_level, str) else target_level)
        except ValueError:
            logger.warning(f"Unknown difficulty level '{target_level}', defaulting to INTERMEDIATE.")
            level = DifficultyLevel.INTERMEDIATE
            
        profile = self.level_profiles[level]
        
        adapted_prompt = f"{prompt}\n\n"
        adapted_prompt += f"--- Difficulty Adaptation: {level.value.upper()} ---\n"
        adapted_prompt += "Please ensure the response adheres to the following constraints:\n"
        adapted_prompt += f"- Vocabulary: {profile['vocabulary']}\n"
        adapted_prompt += f"- Explanation Depth: {profile['explanation_depth']}\n"
        adapted_prompt += f"- Challenge Level: {profile['challenge_level']}\n"
        adapted_prompt += f"- Examples: {profile['examples']}\n"
        adapted_prompt += f"- Exercises: {profile['exercises']}\n"
        
        return adapted_prompt

    def get_level_profile(self, level: DifficultyLevel | str) -> Dict[str, str]:
        """Returns the profile characteristics for a given difficulty level."""
        try:
            enum_level = DifficultyLevel(level.lower() if isinstance(level, str) else level)
            return self.level_profiles[enum_level]
        except ValueError:
            return self.level_profiles[DifficultyLevel.INTERMEDIATE]
