import pytest
from src.optimizer.prompt_optimizer import PromptOptimizer
from src.optimizer.difficulty_adapter import DifficultyAdapter, DifficultyLevel
from src.optimizer.bloom_engine import BloomEngine, BloomLevel
from src.optimizer.prompt_variants import PromptVariantsGenerator, VariantStyle
from src.optimizer.learning_path import LearningPathGenerator
from src.optimizer.prompt_validator import PromptValidator
from src.optimizer.recommendation_engine import RecommendationEngine

def test_prompt_optimizer():
    optimizer = PromptOptimizer()
    prompt = "Please can you tell me what photosynthesis is? I want you to explain it well."
    optimized = optimizer.optimize(prompt)
    assert "Please" not in optimized
    assert "can you" not in optimized
    assert "I want you to" not in optimized
    assert len(optimized) < len(prompt)

def test_difficulty_adapter():
    adapter = DifficultyAdapter()
    prompt = "Explain quantum computing."
    adapted = adapter.adapt(prompt, DifficultyLevel.BEGINNER)
    assert "Difficulty Adaptation: BEGINNER" in adapted
    assert "Use simple, accessible language" in adapted

def test_bloom_engine():
    engine = BloomEngine()
    prompt = engine.generate_prompt("Python", BloomLevel.CREATE)
    assert "CREATE" in prompt
    assert "Bloom's Taxonomy" in prompt

def test_prompt_variants():
    generator = PromptVariantsGenerator()
    variants = generator.generate_variants("Machine Learning", [VariantStyle.QUICK_REVISION, VariantStyle.MCQ_PRACTICE])
    assert len(variants) == 2
    assert variants[0].style == VariantStyle.QUICK_REVISION
    assert variants[1].style == VariantStyle.MCQ_PRACTICE

def test_learning_path_generator():
    generator = LearningPathGenerator()
    prompt = generator.generate_path_prompt("React", "intermediate")
    assert "React" in prompt
    assert "intermediate" in prompt
    assert "JSON" in prompt

def test_prompt_validator():
    validator = PromptValidator()
    # A good prompt
    good_prompt = "Explain how backpropagation works in neural networks. Provide a step-by-step example."
    score_good = validator.validate(good_prompt)
    assert score_good.overall_score > 50

    # A bad prompt
    bad_prompt = "neural net"
    score_bad = validator.validate(bad_prompt)
    assert score_good.overall_score > score_bad.overall_score

def test_recommendation_engine():
    engine = RecommendationEngine()
    validator = PromptValidator()
    prompt = "Explain physics."
    score = validator.validate(prompt)
    recs = engine.generate_recommendations(prompt, "visual", "beginner", score)
    assert len(recs) > 0
    categories = [r.category for r in recs]
    assert "Visual Aids" in categories
    assert "Complexity" in categories
