import json
import pytest
from src.consensus.consensus_builder import ConsensusBuilder, ConsensusBuilderError
from src.models.council_response import CouncilResponse, ResponseMetadata, ResponseScore
from src.models.consensus_result import ConsensusResult


# ==============================================================================
# Helper Factories
# ==============================================================================

def make_mock_response(
    model: str,
    role: str = "creator",
    prompt: str = "Default prompt",
    reasoning: str = "Default reasoning",
    strengths: list[str] = None,
    overall_score: float = 0.8,
) -> CouncilResponse:
    """Create a mock CouncilResponse for testing."""
    if strengths is None:
        strengths = ["Good structure"]
    return CouncilResponse(
        model=model,
        role=role,
        prompt=prompt,
        reasoning=reasoning,
        strengths=strengths,
        metadata=ResponseMetadata(
            tokens_used=100,
            response_time=0.5,
            provider_version=model,
        ),
        score=ResponseScore(
            clarity=overall_score,
            structure=overall_score,
            personalization=overall_score,
            depth=overall_score,
            educational_effectiveness=overall_score,
            overall_score=overall_score,
        )
    )


# ==============================================================================
# Unit Tests
# ==============================================================================

def test_empty_response_list():
    """Verify that an empty response list raises ConsensusBuilderError."""
    builder = ConsensusBuilder()
    with pytest.raises(ConsensusBuilderError, match="cannot be empty"):
        builder.build_consensus([])

    with pytest.raises(ConsensusBuilderError, match="cannot be None"):
        builder.build_consensus(None)


def test_single_response():
    """Verify consensus building on a single response."""
    builder = ConsensusBuilder()
    # Provide a prompt that has some completeness keywords to test the score
    prompt = "Introduction\n\nExplanation\n\nExample\n\nSummary"
    response = make_mock_response(
        model="gpt-4o",
        prompt=prompt,
        reasoning="Simple structure explanation",
        strengths=["Clear logic", "Good pacing"],
        overall_score=0.85,
    )
    result = builder.build_consensus([response], request_id=42, learning_style="visual")

    assert isinstance(result, ConsensusResult)
    assert result.request_id == 42
    # The consensus reasoning is extracted from the single response reasoning
    assert "Simple structure explanation" in result.consensus_reasoning
    assert result.combined_strengths == ["Clear logic", "Good pacing"]
    assert result.contributors == ["gpt-4o"]
    assert result.response_count == 1
    
    # New metric checks
    assert result.winner_model == "gpt-4o"
    assert result.prompt_score == 0.85
    assert result.agreement_score == 1.0 # Single response has 1.0 agreement with itself
    assert result.learning_style_score == 50.0 # Default base score since no visual keywords


def test_highest_weighted_score_selection():
    """Verify that the response with the highest weighted score is selected."""
    builder = ConsensusBuilder()
    
    # R1: High raw score, but low completeness
    r1 = make_mock_response("gpt-4o", prompt="Short prompt", overall_score=0.95)
    
    # R2: Medium raw score, but very complete and aligns with visual learning style
    visual_prompt = "Introduction\n\nHere is a flowchart to visualize\n\nExample\n\nSummary\n\nPractice exercise\n\nConclusion"
    r2 = make_mock_response("claude-3-5-sonnet", prompt=visual_prompt, overall_score=0.80)
    
    # R3: Lowest score
    r3 = make_mock_response("deepseek-chat", prompt="DeepSeek text", overall_score=0.50)
    
    responses = [r1, r2, r3]
    result = builder.build_consensus(responses, learning_style="visual")
    
    # Claude should win due to high learning style (flowchart, visualize) and completeness
    assert result.winner_model == "claude-3-5-sonnet"
    assert visual_prompt in result.final_prompt
    
    # R1 and R3 should have their unique contributions appended to R2's prompt
    assert "Consensus Additions" in result.final_prompt
    assert "gpt-4o" in result.final_prompt
    assert "deepseek-chat" in result.final_prompt


def test_unique_contributions_and_common_concepts():
    """Verify extraction of common concepts and unique contributions."""
    builder = ConsensusBuilder()
    
    r1 = make_mock_response(
        "gpt-4o",
        reasoning="This uses a strong visual analogy and a great conceptual framework.",
        strengths=["Clear visual analogy", "Good pacing"]
    )
    r2 = make_mock_response(
        "claude",
        reasoning="Included a visual analogy as well, plus a hands-on activity.",
        strengths=["Strong visual analogy", "Interactive hands-on activity"]
    )
    
    responses = [r1, r2]
    result = builder.build_consensus(responses)
    
    # "visual" and "analogy" should be common concepts (if > 4 chars)
    # Actually 'visual' and 'analogy' appear in both reasonings/strengths.
    assert "visual" in result.common_concepts
    assert "analogy" in result.common_concepts
    
    # The unique contribution for claude should be the interactive activity
    claude_unique = result.unique_contributions.get("claude", [])
    assert any("activity" in s.lower() for s in claude_unique)


def test_serialization_compatibility():
    """Verify that ConsensusResult can be cleanly converted to a dictionary and serialized to JSON."""
    builder = ConsensusBuilder()
    responses = [
        make_mock_response("gpt-4o", prompt="Selected Prompt", overall_score=0.92)
    ]
    result = builder.build_consensus(responses, request_id=99)
    
    serialized_dict = result.to_dict()
    assert isinstance(serialized_dict, dict)
    assert serialized_dict["request_id"] == 99
    assert serialized_dict["final_prompt"] == "Selected Prompt"
    assert serialized_dict["contributors"] == ["gpt-4o"]
    assert serialized_dict["response_count"] == 1
    assert "best_model" in serialized_dict["response_metadata"]
    
    # Check new fields
    assert "winner_model" in serialized_dict
    assert "overall_consensus_score" in serialized_dict
    assert "failed_providers" in serialized_dict
    
    # Try converting to a JSON string
    json_str = json.dumps(serialized_dict)
    assert isinstance(json_str, str)
    assert "Selected Prompt" in json_str

def test_consensus_score_calculation():
    """Verify the weighted score replaces the old average quality score."""
    builder = ConsensusBuilder()
    # Simple prompts with same text so agreement is 1.0, completeness is 0, style is 0.5
    responses = [
        make_mock_response("gpt-4o", prompt="Text", overall_score=0.8),
        make_mock_response("claude", prompt="Text", overall_score=0.9),
    ]
    result = builder.build_consensus(responses)
    
    # Weighted score for Claude:
    # prompt_score = 0.9 * 0.4 = 0.36
    # agreement = 1.0 * 0.3 = 0.3
    # learning_style = 0.5 * 0.2 = 0.1
    # completeness = 0.0 * 0.1 = 0.0
    # Total = 0.76
    
    assert abs(result.quality_score - 0.76) < 0.01
    assert result.overall_consensus_score == result.quality_score


def test_learning_style_and_completeness():
    """Test specifically the completeness and learning style heuristics."""
    builder = ConsensusBuilder()
    
    prompt = "Introduction\n\nExplanation of the concept.\n\nFor instance, an example.\n\nSummary\n\nLet's do a practice exercise.\n\nConclusion"
    completeness = builder.compute_completeness(prompt)
    assert completeness > 70.0  # Should detect most components (5/7)
    
    # Learning style - visual
    visual_prompt = "Let's look at this diagram and flowchart to visualize."
    visual_score = builder.compute_learning_style_alignment(visual_prompt, "visual")
    assert visual_score == 100.0  # 3 hits: diagram, flowchart, visualize
    
    # Learning style - hands-on
    hands_on_prompt = "Now you try to build a project with this hands-on activity."
    hands_on_score = builder.compute_learning_style_alignment(hands_on_prompt, "hands-on")
    assert hands_on_score == 100.0  # 3+ hits: try, build, project, hands-on, activity


def test_phase3_metrics():
    """Verify Phase 3 explainability and evaluation metrics."""
    builder = ConsensusBuilder()
    
    r1 = make_mock_response("gpt-4o", prompt="Introduction\n\nExample", reasoning="I chose to focus on examples.")
    r2 = make_mock_response("claude", prompt="Theory\n\nAvoid visuals", reasoning="Theory is better.")
    r3 = make_mock_response("gemini", prompt="Introduction\n\nHere are some visuals", reasoning="Visuals are important.")
    
    result = builder.build_consensus([r1, r2, r3], request_id=1, learning_style="visual")
    
    assert result.explanation is not None
    assert "diversity_score" in result.to_dict()
    assert result.diversity_level in ["High", "Medium", "Low"]
    assert "visuals" in result.conflicting_concepts
    
    assert "Introduction" in result.educational_sections
    assert isinstance(result.coverage_score, float)
    
    assert "requested" in result.learning_style_verification
    assert result.learning_style_verification["requested"] == "Visual"
    
    assert result.confidence_level in ["High", "Medium", "Low"]
    assert "consensus" in result.evaluation_summary

