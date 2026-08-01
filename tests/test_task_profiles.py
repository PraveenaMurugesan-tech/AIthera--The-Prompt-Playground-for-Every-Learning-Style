import pytest
from src.workflow.task_profiles import TaskProfileRegistry, ImageGenerationProfile, CodingProfile, LearningProfile, GeneralProfile
from src.workflow.schemas import UniversalInput, DetectedIntent

def test_task_profile_registry():
    assert isinstance(TaskProfileRegistry.get_profile("image_generation"), ImageGenerationProfile)
    assert isinstance(TaskProfileRegistry.get_profile("coding"), CodingProfile)
    assert isinstance(TaskProfileRegistry.get_profile("learning"), LearningProfile)
    
    # Fallback to general
    assert isinstance(TaskProfileRegistry.get_profile("unknown_task"), GeneralProfile)

def test_image_generation_profile():
    profile = ImageGenerationProfile()
    input_data = UniversalInput(raw_content="A futuristic city", input_type="text")
    intent = DetectedIntent(intent="create", task_type="image_generation", domain="art", subject="city")
    
    prompt = profile.build_prompt(input_data, intent)
    assert "futuristic city" in prompt
    assert "image generator" in prompt
    assert "Domain: art" in prompt
    
    # Provider suitability
    assert profile.get_provider_suitability("Gemini") == 0.9
    assert profile.get_provider_suitability("SambaNova") == 0.5
    assert profile.get_provider_suitability("Unknown") == 0.5

def test_coding_profile():
    profile = CodingProfile()
    input_data = UniversalInput(raw_content="Write a python script", input_type="text")
    intent = DetectedIntent(intent="code", task_type="coding", domain="software", subject="python script")
    
    prompt = profile.build_prompt(input_data, intent)
    assert "Write a python script" in prompt
    assert "expert software engineer" in prompt
    
    # Provider suitability
    assert profile.get_provider_suitability("Claude") == 0.95
    assert profile.get_provider_suitability("Groq") == 0.8

def test_learning_profile():
    profile = LearningProfile()
    input_data = UniversalInput(raw_content="Explain quantum physics", input_type="text")
    intent = DetectedIntent(intent="learn", task_type="learning", domain="science", subject="quantum physics")
    
    prompt = profile.build_prompt(input_data, intent)
    assert "Explain quantum physics" in prompt
    assert "expert educator" in prompt

def test_general_profile():
    profile = GeneralProfile()
    input_data = UniversalInput(raw_content="Hello there", input_type="text")
    intent = DetectedIntent(intent="chat", task_type="general", domain="general", subject="greeting")
    
    prompt = profile.build_prompt(input_data, intent)
    assert "Hello there" in prompt
    assert "helpful AI assistant" in prompt
