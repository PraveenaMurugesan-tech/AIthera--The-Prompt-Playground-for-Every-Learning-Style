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
    response = make_mock_response(
        model="gpt-4o",
        prompt="Single provider prompt",
        reasoning="Simple structure explanation",
        strengths=["Clear logic", "Good pacing"],
        overall_score=0.85,
    )
    result = builder.build_consensus([response], request_id=42)

    assert isinstance(result, ConsensusResult)
    assert result.request_id == 42
    assert result.final_prompt == "Single provider prompt"
    assert "GPT provided strong educational structure" in result.consensus_reasoning
    assert result.combined_strengths == ["Clear logic", "Good pacing"]
    assert result.quality_score == 0.85
    assert result.contributors == ["gpt"]
    assert result.response_count == 1


def test_multiple_responses():
    """Verify consensus building on multiple valid responses."""
    builder = ConsensusBuilder()
    responses = [
        make_mock_response("gpt-4o", prompt="GPT Prompt", overall_score=0.8),
        make_mock_response("claude-3-5-sonnet", prompt="Claude Prompt", overall_score=0.9),
        make_mock_response("gemini-1.5-pro", prompt="Gemini Prompt", overall_score=0.7),
    ]
    result = builder.build_consensus(responses)

    assert isinstance(result, ConsensusResult)
    assert result.final_prompt == "Claude Prompt"  # Claude had the highest score
    assert result.quality_score == 0.8  # Average of 0.8, 0.9, 0.7 = 0.8
    assert set(result.contributors) == {"gpt", "claude", "gemini"}
    assert result.response_count == 3


def test_highest_score_selection():
    """Verify that the response with the highest score is selected."""
    builder = ConsensusBuilder()
    responses = [
        make_mock_response("gpt-4o", prompt="GPT", overall_score=0.75),
        make_mock_response("claude-3-5-sonnet", prompt="Claude", overall_score=0.82),
        make_mock_response("deepseek-chat", prompt="DeepSeek", overall_score=0.95),
    ]
    result = builder.build_consensus(responses)
    assert result.final_prompt == "DeepSeek"


def test_tie_breaking_logic():
    """Verify priority-based tie-breaking when overall scores match.

    Priority: GPT > Claude > Gemini > DeepSeek
    """
    builder = ConsensusBuilder()

    # Tie 1: GPT (priority 4) vs Claude (priority 3) -> GPT wins
    responses1 = [
        make_mock_response("claude-3-5-sonnet", prompt="Claude Tie", overall_score=0.9),
        make_mock_response("gpt-4o", prompt="GPT Tie", overall_score=0.9),
    ]
    result1 = builder.build_consensus(responses1)
    assert result1.final_prompt == "GPT Tie"

    # Tie 2: Gemini (priority 2) vs DeepSeek (priority 1) -> Gemini wins
    responses2 = [
        make_mock_response("deepseek-chat", prompt="DeepSeek Tie", overall_score=0.85),
        make_mock_response("gemini-1.5-pro", prompt="Gemini Tie", overall_score=0.85),
    ]
    result2 = builder.build_consensus(responses2)
    assert result2.final_prompt == "Gemini Tie"

    # Tie 3: Claude (priority 3) vs DeepSeek (priority 1) -> Claude wins
    responses3 = [
        make_mock_response("deepseek-chat", prompt="DeepSeek Tie 2", overall_score=0.88),
        make_mock_response("claude-3-5-sonnet", prompt="Claude Tie 2", overall_score=0.88),
    ]
    result3 = builder.build_consensus(responses3)
    assert result3.final_prompt == "Claude Tie 2"


def test_strength_aggregation():
    """Verify unique, non-empty strength aggregation preserving order and ignoring whitespaces."""
    builder = ConsensusBuilder()
    r1 = make_mock_response("gpt-4o", strengths=["Strength A"])
    r1.strengths = ["  ", "Strength A", "Strength B"]

    r2 = make_mock_response("claude-3-5-sonnet", strengths=["Strength B"])
    r2.strengths = ["Strength B", "", "Strength C"]

    r3 = make_mock_response("gemini-1.5-pro", strengths=["Strength A"])
    r3.strengths = ["Strength A", "  Strength D  "]

    responses = [r1, r2, r3]
    strengths = builder.aggregate_strengths(responses)
    # Expected: Strength A, Strength B, Strength C, Strength D
    assert strengths == ["Strength A", "Strength B", "Strength C", "Strength D"]


def test_consensus_score_calculation():
    """Verify average score calculation and rounding to 2 decimals."""
    builder = ConsensusBuilder()
    responses = [
        make_mock_response("gpt-4o", overall_score=0.883),
        make_mock_response("claude-3-5-sonnet", overall_score=0.912),
        make_mock_response("gemini-1.5-pro", overall_score=0.745),
    ]
    # Average: (0.883 + 0.912 + 0.745) / 3 = 0.846666... -> 0.85
    result = builder.build_consensus(responses)
    assert result.quality_score == 0.85


def test_contributor_extraction():
    """Verify contributor tracking filters and maps provider keys correctly."""
    builder = ConsensusBuilder()
    r5 = make_mock_response("gpt-4o-mini")
    r5.model = "unknown-model-xyz"

    responses = [
        make_mock_response("gpt-4o-mini"),
        make_mock_response("claude-3-5-sonnet"),
        make_mock_response("gemini-2.0-flash"),
        make_mock_response("deepseek-reasoner"),
        r5,
    ]
    contributors = builder.extract_contributors(responses)
    assert contributors == ["gpt", "claude", "gemini", "deepseek"]


def test_consensus_reasoning_generation():
    """Verify generation of consensus reasoning based on contributing models."""
    builder = ConsensusBuilder()
    
    # All four providers
    responses_all = [
        make_mock_response("gpt-4o"),
        make_mock_response("claude-3"),
        make_mock_response("gemini-1.5"),
        make_mock_response("deepseek-chat"),
    ]
    reasoning_all = builder.generate_consensus_reasoning(
        responses_all, responses_all[0], ["Strength 1"]
    )
    assert "GPT provided strong educational structure while Claude contributed deeper reasoning" in reasoning_all
    assert "Gemini improved visualization and DeepSeek strengthened logical flow" in reasoning_all
    assert "The final prompt was selected based on the highest quality score." in reasoning_all

    # Only GPT and Gemini
    responses_partial = [
        make_mock_response("gpt-4o"),
        make_mock_response("gemini-1.5"),
    ]
    reasoning_partial = builder.generate_consensus_reasoning(
        responses_partial, responses_partial[0], ["Strength 1"]
    )
    assert "GPT provided strong educational structure" in reasoning_partial
    assert "Gemini improved visualization" in reasoning_partial
    assert "Claude" not in reasoning_partial
    assert "DeepSeek" not in reasoning_partial


def test_invalid_response_object():
    """Verify that invalid response objects raise ConsensusBuilderError."""
    builder = ConsensusBuilder()
    
    # Non-CouncilResponse instance in list
    with pytest.raises(ConsensusBuilderError, match="All elements must be CouncilResponse instances"):
        builder.build_consensus([{"model": "gpt-4o", "prompt": "invalid type"}])

    # None value in list
    with pytest.raises(ConsensusBuilderError, match="All elements must be CouncilResponse instances"):
        builder.build_consensus([None])


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
    assert serialized_dict["quality_score"] == 0.92
    assert serialized_dict["contributors"] == ["gpt"]
    assert serialized_dict["response_count"] == 1
    assert "best_model" in serialized_dict["response_metadata"]
    
    # Try converting to a JSON string
    json_str = json.dumps(serialized_dict)
    assert isinstance(json_str, str)
    assert "Selected Prompt" in json_str
