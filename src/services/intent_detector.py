import logging
from typing import Dict, Any, Optional

from src.workflow.schemas import UniversalInput, DetectedIntent
from src.providers.provider_registry import ProviderRegistry

logger = logging.getLogger(__name__)

class IntentDetector:
    """Uses a fast AI provider to determine the user's intent from universal inputs."""
    
    def __init__(self, registry: ProviderRegistry, default_provider: str = "groq"):
        self.registry = registry
        self.default_provider = default_provider
        self.system_prompt = (
            "You are an intent detection engine. Based on the user's input, determine their intent. "
            "Output valid JSON ONLY matching the following schema: "
            '{"intent": "str", "domain": "str", "task_type": "str", "subject": "str", "style": "str|null", "output_type": "str|null"}. '
            "IMPORTANT: 'task_type' MUST be exactly one of: "
            "['image_generation', 'image_analysis', 'coding', 'research', 'summarization', "
            "'learning', 'creative_writing', 'marketing', 'data_analysis', 'presentation', "
            "'planning', 'translation', 'general']. "
            "Do not include markdown blocks or any other text."
        )

    async def detect_intent(self, input_data: UniversalInput) -> DetectedIntent:
        provider = self.registry.get_provider(self.default_provider)
        
        content = f"Input type: {input_data.input_type}\n"
        if input_data.raw_content:
            content += f"Content: {input_data.raw_content}\n"
        if input_data.transcript:
            content += f"Transcript: {input_data.transcript}\n"
            
        full_prompt = f"{self.system_prompt}\n\nUser Input:\n{content}"
        
        try:
            # We call the provider's generate_response method with empty required args 
            # and pass the prompt directly to bypass the template.
            response = await provider.generate_response(
                topic="",
                objective="",
                learning_style="",
                difficulty="",
                education_level="",
                output_length="",
                prompt=full_prompt
            )
            
            import json
            import re
            
            # extract the text from raw_response dict
            if isinstance(response, dict) and "choices" in response:
                text = response["choices"][0]["message"]["content"]
            else:
                text = str(response)
                
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group(0)
                
            data = json.loads(text)
            return DetectedIntent(**data)
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            # Fallback to general intent
            return DetectedIntent(
                intent="general",
                domain="general",
                task_type="general",
                subject=input_data.raw_content or "unknown"
            )
