from typing import Dict, Any, Optional
from src.workflow.schemas import UniversalInput

class InputNormalizer:
    """Normalizes various frontend requests into a single UniversalInput."""
    
    @staticmethod
    def from_text(topic: str, metadata: Optional[Dict[str, Any]] = None) -> UniversalInput:
        return UniversalInput(
            input_type="text",
            raw_content=topic,
            metadata=metadata or {}
        )
        
    @staticmethod
    def from_voice(transcript: str, metadata: Optional[Dict[str, Any]] = None) -> UniversalInput:
        return UniversalInput(
            input_type="voice",
            transcript=transcript,
            raw_content=transcript,  # Keep raw content as fallback
            metadata=metadata or {}
        )
        
    @staticmethod
    def from_image(image_data: str, instructions: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> UniversalInput:
        return UniversalInput(
            input_type="image",
            image_data=image_data,
            raw_content=instructions,
            metadata=metadata or {}
        )
