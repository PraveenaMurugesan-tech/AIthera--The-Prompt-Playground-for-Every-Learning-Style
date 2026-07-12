import logging
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("aithera.prompt_variants")

class VariantStyle(str, Enum):
    QUICK_REVISION = "quick_revision"
    INTERVIEW_PREP = "interview_preparation"
    CODING_PRACTICE = "coding_practice"
    PROJECT_BASED = "project_based"
    MCQ_PRACTICE = "mcq_practice"
    DEEP_EXPLANATION = "deep_explanation"
    EXAM_PREP = "exam_preparation"
    REAL_WORLD = "real_world_application"

class PromptVariant(BaseModel):
    """Structured representation of a prompt variant."""
    style: VariantStyle = Field(..., description="The style of the variant")
    title: str = Field(..., description="A short, descriptive title for the variant")
    prompt_text: str = Field(..., description="The generated prompt text")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata about the variant")

class PromptVariantsGenerator:
    """Generates multiple style variants for a single prompt/topic."""
    
    def __init__(self):
        self.style_prompts = {
            VariantStyle.QUICK_REVISION: "Create a concise summary and 3 rapid-fire questions to quickly revise the topic.",
            VariantStyle.INTERVIEW_PREP: "Act as a technical interviewer. Ask a common interview question related to this topic and evaluate the user's response.",
            VariantStyle.CODING_PRACTICE: "Provide a coding challenge related to this topic, including starter code and expected output.",
            VariantStyle.PROJECT_BASED: "Design a mini-project that requires applying the concepts of this topic to build a working prototype.",
            VariantStyle.MCQ_PRACTICE: "Generate 5 multiple-choice questions about this topic, varying in difficulty. Do not provide the answers immediately.",
            VariantStyle.DEEP_EXPLANATION: "Provide a comprehensive, deep-dive explanation of this topic, including historical context, theoretical foundations, and edge cases.",
            VariantStyle.EXAM_PREP: "Create a rigorous exam-style question (e.g., essay or complex problem) that tests deep understanding of the topic.",
            VariantStyle.REAL_WORLD: "Present a real-world case study or scenario where this topic is critical to solving a business or engineering problem."
        }

    def generate_variants(self, base_topic: str, styles: Optional[List[VariantStyle]] = None) -> List[PromptVariant]:
        """
        Generates prompt variants for the given topic and styles.
        If styles is None, generates all available variants.
        
        Args:
            base_topic: The topic to generate variants for.
            styles: A list of VariantStyle enums to generate.
            
        Returns:
            A list of PromptVariant objects.
        """
        if not styles:
            styles = list(VariantStyle)
            
        variants = []
        for style in styles:
            instruction = self.style_prompts.get(style, "")
            
            # Construct the variant prompt
            prompt_text = f"Topic: {base_topic}\n\nTask: {instruction}\n\nPlease adapt your teaching style to match this specific format."
            
            variant = PromptVariant(
                style=style,
                title=f"{style.value.replace('_', ' ').title()} - {base_topic[:20]}...",
                prompt_text=prompt_text,
                metadata={"base_topic": base_topic}
            )
            variants.append(variant)
            
        logger.info(f"Generated {len(variants)} prompt variants for topic '{base_topic}'")
        return variants
