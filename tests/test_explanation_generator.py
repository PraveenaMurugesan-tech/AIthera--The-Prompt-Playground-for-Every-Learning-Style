"""Unit tests for Explanation Generator."""

import json
import pytest

from src.explanation.explanation_generator import ExplanationGenerator, ExplanationGenerationError
from src.models.consensus_result import ConsensusResult
from src.scoring.prompt_scorer import ResponseScore


def test_provider_explanations_single():
    generator = ExplanationGenerator()
    
    # Test single contributors
    res_gpt = generator.generate_provider_explanation(["gpt"])
    assert "GPT contributed educational structure and prompt organization." in res_gpt

    res_claude = generator.generate_provider_explanation(["claude"])
    assert "Claude enhanced reasoning depth and analytical thinking." in res_claude

    res_gemini = generator.generate_provider_explanation(["gemini"])
    assert "Gemini provided visual learning support and concept visualization." in res_gemini

    res_deepseek = generator.generate_provider_explanation(["deepseek"])
    assert "DeepSeek added technical precision and logical accuracy." in res_deepseek


def test_provider_explanations_multiple():
    generator = ExplanationGenerator()
    
    # Test multiple contributors
    res_two = generator.generate_provider_explanation(["gpt", "claude"])
    assert res_two == "GPT contributed educational structure while Claude enhanced reasoning depth."

    res_three = generator.generate_provider_explanation(["gpt", "claude", "gemini"])
    assert res_three == "GPT contributed educational structure, Claude enhanced reasoning depth, while Gemini provided visual learning support."

    res_four = generator.generate_provider_explanation(["gpt", "claude", "gemini", "deepseek"])
    assert res_four == "GPT contributed educational structure, Claude enhanced reasoning depth, Gemini provided visual learning support, while DeepSeek added technical precision."


def test_provider_explanation_case_insensitive_and_versions():
    generator = ExplanationGenerator()
    res = generator.generate_provider_explanation(["GPT-4o", "claude-3-5-sonnet"])
    assert res == "GPT contributed educational structure while Claude enhanced reasoning depth."


def test_consensus_explanation_generation():
    generator = ExplanationGenerator()
    
    consensus = ConsensusResult(
        contributors=["gpt", "claude"],
        combined_strengths=["strong pedagogy", "detailed structure"],
        response_count=2,
        consensus_reasoning="The prompt from Claude offered superior depth while GPT provided clean educational scaffolding.",
        quality_score=85.0
    )
    
    explanation = generator.generate_consensus_explanation(consensus)
    
    assert "pool of 2 candidate responses" in explanation
    assert "quality score of 85.00" in explanation
    assert "strong pedagogy, detailed structure" in explanation
    assert "GPT contributed educational structure while Claude enhanced reasoning depth." in explanation
    assert "The prompt from Claude offered superior depth" in explanation


def test_learning_style_explanations():
    generator = ExplanationGenerator()
    
    assert "diagrams" in generator.generate_learning_style_explanation("visual")
    assert "discussion" in generator.generate_learning_style_explanation("conversational")
    assert "sequential actions" in generator.generate_learning_style_explanation("step-by-step")
    assert "sequential actions" in generator.generate_learning_style_explanation("step_by_step")
    assert "high-yield" in generator.generate_learning_style_explanation("exam-focused")
    assert "evidence-based" in generator.generate_learning_style_explanation("research-oriented")


def test_score_explanations_classifications():
    generator = ExplanationGenerator()
    
    # Excellent
    score_exc = ResponseScore(
        clarity=19.0, structure=18.0, personalization=19.0,
        educational_effectiveness=19.0, depth=18.0, overall_score=93.0,
        classification="Excellent"
    )
    explanation = generator.generate_score_explanation(score_exc)
    assert "achieved an Excellent rating" in explanation
    assert "clarity" in explanation
    assert "structure" in explanation
    assert "personalization" in explanation

    # Good
    score_good = ResponseScore(
        clarity=16.0, structure=15.0, personalization=16.0,
        educational_effectiveness=16.0, depth=15.0, overall_score=78.0,
        classification="Good"
    )
    explanation = generator.generate_score_explanation(score_good)
    assert "achieved a Good rating" in explanation

    # Average / Fair
    score_fair = ResponseScore(
        clarity=12.0, structure=13.0, personalization=12.0,
        educational_effectiveness=12.0, depth=12.0, overall_score=61.0,
        classification="Fair"
    )
    explanation = generator.generate_score_explanation(score_fair)
    assert "achieved an Average rating" in explanation

    # Poor
    score_poor = ResponseScore(
        clarity=8.0, structure=7.0, personalization=9.0,
        educational_effectiveness=8.0, depth=8.0, overall_score=40.0,
        classification="Poor"
    )
    explanation = generator.generate_score_explanation(score_poor)
    assert "achieved a Poor rating" in explanation


def test_score_explanation_inference():
    generator = ExplanationGenerator()
    # Missing classification but has overall_score
    score_no_class = ResponseScore(
        clarity=19.0, structure=18.0, personalization=19.0,
        educational_effectiveness=19.0, depth=18.0, overall_score=93.0,
        classification=None
    )
    explanation = generator.generate_score_explanation(score_no_class)
    assert "Excellent" in explanation


def test_full_explanation_output():
    generator = ExplanationGenerator()
    consensus = ConsensusResult(
        contributors=["gpt", "deepseek"],
        combined_strengths=["technical precision", "structure"],
        response_count=2,
        consensus_reasoning="Combined technical aspects with clean structure.",
        quality_score=90.0
    )
    score = ResponseScore(
        clarity=19.0, structure=19.0, personalization=18.0,
        educational_effectiveness=18.0, depth=18.0, overall_score=92.0,
        classification="Excellent"
    )
    
    full_exp = generator.generate_full_explanation(
        consensus_result=consensus,
        score=score,
        learning_style="research-oriented"
    )
    
    assert isinstance(full_exp, dict)
    assert "provider_explanation" in full_exp
    assert "consensus_explanation" in full_exp
    assert "learning_style_explanation" in full_exp
    assert "score_explanation" in full_exp
    assert "summary" in full_exp

    assert "GPT contributed educational structure while DeepSeek added technical precision." in full_exp["provider_explanation"]
    assert "research-oriented" in full_exp["summary"]
    assert "Excellent" in full_exp["summary"]


def test_serialization_compatibility():
    generator = ExplanationGenerator()
    
    consensus_dict = {
        "contributors": ["gpt", "claude"],
        "combined_strengths": ["clarity"],
        "response_count": 2,
        "consensus_reasoning": "Simple win reasoning.",
        "quality_score": 85.0
    }
    
    score_dict = {
        "clarity": 18.0,
        "structure": 17.0,
        "personalization": 18.0,
        "educational_effectiveness": 16.0,
        "depth": 16.0,
        "overall_score": 85.0,
        "classification": "Good"
    }

    full_exp = generator.generate_full_explanation(
        consensus_result=consensus_dict,
        score=score_dict,
        learning_style="visual"
    )
    
    # Ensure it serializes to JSON without issues
    json_str = json.dumps(full_exp)
    assert isinstance(json_str, str)


def test_invalid_inputs_and_exceptions():
    generator = ExplanationGenerator()
    
    # Invalid contributors list
    with pytest.raises(ExplanationGenerationError):
        generator.generate_provider_explanation(None)
    with pytest.raises(ExplanationGenerationError):
        generator.generate_provider_explanation("not-a-list")
    with pytest.raises(ExplanationGenerationError):
        generator.generate_provider_explanation([])
    with pytest.raises(ExplanationGenerationError):
        generator.generate_provider_explanation([123])

    # Unknown providers should trigger a fallback, not an exception
    res_generic = generator.generate_provider_explanation(["unknown-provider"])
    assert "Unknown-provider provided general capabilities" in res_generic

    # Invalid learning style
    with pytest.raises(ExplanationGenerationError):
        generator.generate_learning_style_explanation(None)
    with pytest.raises(ExplanationGenerationError):
        generator.generate_learning_style_explanation(123)
    with pytest.raises(ExplanationGenerationError):
        generator.generate_learning_style_explanation("not-a-supported-style")

    # Invalid ConsensusResult
    with pytest.raises(ExplanationGenerationError):
        generator.generate_consensus_explanation(None)
    
    malformed_consensus = {"response_count": "not-an-int"}
    with pytest.raises(ExplanationGenerationError):
        generator.generate_consensus_explanation(malformed_consensus)

    # Invalid ResponseScore
    with pytest.raises(ExplanationGenerationError):
        generator.generate_score_explanation(None)
        
    malformed_score = {}
    with pytest.raises(ExplanationGenerationError):
        generator.generate_score_explanation(malformed_score)
