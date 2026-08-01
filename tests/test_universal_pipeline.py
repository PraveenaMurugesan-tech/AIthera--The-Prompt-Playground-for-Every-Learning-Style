import pytest
import json
from src.workflow.schemas import UniversalInput
from src.workflow.normalizer import InputNormalizer
from src.services.intent_detector import IntentDetector, DetectedIntent

def test_text_normalization():
    topic = "Create a cinematic wallpaper of Bangalore in 2050."
    metadata = {"source": "web"}
    result = InputNormalizer.from_text(topic, metadata)
    assert result.input_type == "text"
    assert result.raw_content == topic
    assert result.metadata == metadata

def test_voice_normalization():
    transcript = "Explain quantum computing like I'm 12."
    result = InputNormalizer.from_voice(transcript)
    assert result.input_type == "voice"
    assert result.transcript == transcript
    assert result.raw_content == transcript

def test_image_normalization():
    image_data = "base64_encoded_string"
    instructions = "Make it look like this but cyberpunk"
    result = InputNormalizer.from_image(image_data, instructions)
    assert result.input_type == "image"
    assert result.image_data == image_data
    assert result.raw_content == instructions

@pytest.mark.anyio
async def test_intent_detector_fallback():
    # Mock registry and provider
    class MockProvider:
        async def generate_response(self, *args, **kwargs):
            raise Exception("Provider failed")
            
    class MockRegistry:
        def get_provider(self, name):
            return MockProvider()
            
    detector = IntentDetector(MockRegistry())
    input_data = InputNormalizer.from_text("Test fallback")
    
    result = await detector.detect_intent(input_data)
    assert result.intent == "general"
    assert result.task_type == "general"

@pytest.mark.anyio
async def test_intent_detector_success():
    # Mock a successful JSON response
    class MockProvider:
        async def generate_response(self, *args, **kwargs):
            return {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "intent": "create",
                            "domain": "creative",
                            "task_type": "image_generation",
                            "subject": "cinematic wallpaper"
                        })
                    }
                }]
            }
            
    class MockRegistry:
        def get_provider(self, name):
            return MockProvider()
            
    detector = IntentDetector(MockRegistry())
    input_data = InputNormalizer.from_text("Create a cinematic poster")
    
    result = await detector.detect_intent(input_data)
    assert result.intent == "create"
    assert result.task_type == "image_generation"
