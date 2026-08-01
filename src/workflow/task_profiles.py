from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from src.workflow.schemas import UniversalInput, DetectedIntent


class BaseTaskProfile(ABC):
    """
    Abstract base class for all Task Profiles.
    Defines the shape and expectations for specific prompt engineering tasks.
    """
    
    task_type: str = "general"
    purpose: str = "General processing"
    required_fields: List[str] = []
    optional_fields: List[str] = []
    
    # Maps provider_name to a suitability score (0.0 to 1.0)
    # 1.0 = highly recommended for this task
    # 0.0 = not recommended (but not completely disabled)
    recommended_providers: Dict[str, float] = {}
    
    # Custom scoring priorities to override the default prompt scorer
    scoring_priorities: Dict[str, float] = {
        "clarity": 0.25,
        "structure": 0.20,
        "personalization": 0.20,
        "educational_effectiveness": 0.25,
        "depth": 0.10,
    }

    def get_provider_suitability(self, provider_name: str) -> float:
        """Returns the suitability score for a given provider for this task."""
        # Default suitability is 0.5 if not explicitly configured
        return self.recommended_providers.get(provider_name, 0.5)

    @abstractmethod
    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        """
        Construct an optimized prompt for the provider based on the universal input.
        """
        pass


class ImageGenerationProfile(BaseTaskProfile):
    task_type = "image_generation"
    purpose = "Generates highly descriptive prompts for text-to-image models"
    recommended_providers = {
        "Gemini": 0.9,
        "Claude": 0.9,
        "GPT": 0.8,
        "Groq": 0.6,
        "DeepSeek": 0.6,
        "OpenRouter": 0.8,
        "Cerebras": 0.5,
        "SambaNova": 0.5
    }
    scoring_priorities = {
        "clarity": 0.30,
        "structure": 0.20,
        "personalization": 0.10,
        "educational_effectiveness": 0.0, # Not applicable
        "depth": 0.40, # Deep visual details
    }

    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        base = (
            "You are an expert AI image prompt engineer. Your goal is to take the user's intent "
            "and create a highly detailed, evocative, and structurally perfect prompt for an image generator (like Midjourney or DALL-E).\n\n"
        )
        if input_data.raw_content:
            base += f"User Request: {input_data.raw_content}\n"
        if intent.domain:
            base += f"Domain: {intent.domain}\n"
            
        base += (
            "\nPlease write a comprehensive image generation prompt. Include details about:\n"
            "- Subject and action\n"
            "- Lighting and mood\n"
            "- Camera angle, lens, or perspective\n"
            "- Artistic style or medium\n"
            "Return ONLY the image generation prompt text, no pleasantries or explanation."
        )
        return base


class CodingProfile(BaseTaskProfile):
    task_type = "coding"
    purpose = "Generates technical programming prompts"
    recommended_providers = {
        "Claude": 0.95,
        "DeepSeek": 0.95,
        "GPT": 0.9,
        "Gemini": 0.85,
        "Groq": 0.8,
        "OpenRouter": 0.9,
        "Cerebras": 0.7,
        "SambaNova": 0.7
    }
    scoring_priorities = {
        "clarity": 0.30,
        "structure": 0.30,
        "personalization": 0.05,
        "educational_effectiveness": 0.05,
        "depth": 0.30, # Technical accuracy
    }

    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        base = (
            "You are an expert software engineer. Your task is to provide clean, optimized, and fully functioning code.\n\n"
        )
        if input_data.raw_content:
            base += f"Task: {input_data.raw_content}\n"
        
        base += (
            "\nPlease provide the solution. Include:\n"
            "- A brief explanation of the approach\n"
            "- The code blocks (properly formatted)\n"
            "- Any necessary tests or edge cases handled\n"
        )
        return base


class LearningProfile(BaseTaskProfile):
    task_type = "learning"
    purpose = "Legacy educational engine behavior"
    recommended_providers = {
        "Groq": 0.9,
        "Claude": 0.9,
        "GPT": 0.9,
        "Gemini": 0.8,
        "DeepSeek": 0.8,
        "OpenRouter": 0.8,
        "Cerebras": 0.8,
        "SambaNova": 0.8
    }
    # Keeps default educational priorities
    
    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        # For learning profiles, the CouncilExecutor will still use the old 
        # template-based injection if we return None or a specific flag.
        # Alternatively, we can just return the raw text if they didn't provide kwargs.
        if not input_data.raw_content:
            return "Please provide an educational lesson."
            
        return (
            "You are an expert educator. Create an interactive and engaging educational response.\n"
            f"Topic/Request: {input_data.raw_content}\n"
            "Ensure it is highly structured, clear, and pedagogically effective."
        )


class GeneralProfile(BaseTaskProfile):
    task_type = "general"
    purpose = "Fallback for unrecognized or general conversational intents"
    
    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        return (
            "You are a helpful AI assistant. Please respond to the following request comprehensively.\n\n"
            f"Request: {input_data.raw_content or ''}"
        )


class ImageAnalysisProfile(BaseTaskProfile):
    task_type = "image_analysis"
    purpose = "Analyzes an image and generates an optimized prompt or educational breakdown based on it."
    recommended_providers = {
        "Gemini": 1.0,
        "Claude": 0.9,
        "GPT": 0.9,
    }
    scoring_priorities = {
        "clarity": 0.30,
        "structure": 0.30,
        "personalization": 0.10,
        "educational_effectiveness": 0.10,
        "depth": 0.20,
    }

    def build_prompt(self, input_data: UniversalInput, intent: DetectedIntent) -> str:
        base = (
            "You are an expert image analyst and educator. Your goal is to analyze the provided image data "
            "and extract its core educational topic or subject. "
        )
        if input_data.raw_content:
            base += f"User Instructions: {input_data.raw_content}\n"
        
        base += (
            "\nPlease write a comprehensive breakdown of the image. If the user provided instructions, fulfill them using the image as context.\n"
            "Include:\n"
            "- The main subject or topic\n"
            "- Key details and visual structure\n"
            "- Educational context or significance\n"
        )
        return base


class TaskProfileRegistry:
    """Factory to map intent task types to specific profiles."""
    
    _profiles = {
        "image_generation": ImageGenerationProfile(),
        "image_analysis": ImageAnalysisProfile(),
        "coding": CodingProfile(),
        "learning": LearningProfile(),
        "general": GeneralProfile()
    }
    
    @classmethod
    def get_profile(cls, task_type: str) -> BaseTaskProfile:
        return cls._profiles.get(task_type, cls._profiles["general"])
