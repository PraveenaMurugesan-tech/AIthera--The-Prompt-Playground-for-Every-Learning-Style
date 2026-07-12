import logging
from enum import Enum
from typing import Dict, List, Any

logger = logging.getLogger("aithera.bloom_engine")

class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class BloomEngine:
    """Generates educational prompts aligned with Bloom's Taxonomy."""
    
    def __init__(self):
        self.level_prompts = {
            BloomLevel.REMEMBER: {
                "verbs": ["define", "list", "memorize", "repeat", "state", "recall", "name"],
                "instruction": "Focus on retrieving, recognizing, and recalling relevant knowledge from long-term memory. Ask the user to define terms or list key facts.",
                "example_question": "What are the core components of [Topic]?"
            },
            BloomLevel.UNDERSTAND: {
                "verbs": ["classify", "describe", "discuss", "explain", "identify", "locate", "recognize", "report", "select", "translate"],
                "instruction": "Focus on constructing meaning from instructional messages. Ask the user to explain ideas or concepts in their own words.",
                "example_question": "How would you explain [Topic] to a peer?"
            },
            BloomLevel.APPLY: {
                "verbs": ["execute", "implement", "solve", "use", "demonstrate", "interpret", "operate", "schedule", "sketch"],
                "instruction": "Focus on carrying out or using a procedure in a given situation. Ask the user to use information in new situations.",
                "example_question": "How would you use [Topic] to solve [Problem]?"
            },
            BloomLevel.ANALYZE: {
                "verbs": ["differentiate", "organize", "attribute", "compare", "contrast", "distinguish", "examine", "experiment", "question", "test"],
                "instruction": "Focus on breaking material into constituent parts, determining how the parts relate to one another and to an overall structure or purpose. Ask the user to draw connections among ideas.",
                "example_question": "What is the relationship between [Part A] and [Part B] within [Topic]?"
            },
            BloomLevel.EVALUATE: {
                "verbs": ["appraise", "argue", "defend", "judge", "select", "support", "value", "critique", "weigh"],
                "instruction": "Focus on making judgments based on criteria and standards. Ask the user to justify a stand or decision.",
                "example_question": "Do you agree with [Approach] for handling [Topic]? Why or why not?"
            },
            BloomLevel.CREATE: {
                "verbs": ["design", "assemble", "construct", "conjecture", "develop", "formulate", "author", "investigate"],
                "instruction": "Focus on putting elements together to form a coherent or functional whole; reorganizing elements into a new pattern or structure. Ask the user to produce new or original work.",
                "example_question": "Design a new [System/Solution] using the principles of [Topic]."
            }
        }

    def generate_prompt(self, base_topic: str, level: BloomLevel | str) -> str:
        """
        Generates a prompt template targeted at a specific Bloom's Taxonomy level.
        
        Args:
            base_topic: The subject matter topic.
            level: The target Bloom's Taxonomy level.
            
        Returns:
            A prompt specifically designed to target the cognitive skills of the specified level.
        """
        try:
            target_level = BloomLevel(level.lower() if isinstance(level, str) else level)
        except ValueError:
            logger.warning(f"Unknown Bloom level '{level}', defaulting to UNDERSTAND.")
            target_level = BloomLevel.UNDERSTAND
            
        profile = self.level_prompts[target_level]
        
        prompt = f"Design an educational interaction about '{base_topic}' that targets the '{target_level.value.upper()}' level of Bloom's Taxonomy.\n\n"
        prompt += f"Pedagogical Goal: {profile['instruction']}\n"
        prompt += f"Suggested Action Verbs: {', '.join(profile['verbs'])}\n"
        prompt += f"Example Approach: {profile['example_question'].replace('[Topic]', base_topic)}\n\n"
        prompt += "Ensure that the tasks, questions, and feedback you generate strictly align with this cognitive level. Do not ask for simple recall if the level is 'Analyze', and do not ask for complex synthesis if the level is 'Remember'."
        
        return prompt

    def get_helper_methods(self, level: BloomLevel | str) -> Dict[str, Any]: # Using dict to avoid importing Any for now, wait I should fix that
        """Returns the helper metadata for a given Bloom's level."""
        try:
            target_level = BloomLevel(level.lower() if isinstance(level, str) else level)
            return self.level_prompts[target_level]
        except ValueError:
            return self.level_prompts[BloomLevel.UNDERSTAND]
