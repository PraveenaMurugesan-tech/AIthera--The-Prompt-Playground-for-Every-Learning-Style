"""
Unit tests for Prompt Scorer.
"""

import json
import pytest

from src.models.consensus_result import ConsensusResult
from src.models.prompt_request import PromptRequest
from src.models.explanation import Explanation
from src.scoring.prompt_scorer import PromptScorer, PromptScoringError, ResponseScore


def create_mock_consensus(prompt: str, learning_style: str = "visual") -> ConsensusResult:
    """Helper to create an in-memory ConsensusResult with a linked PromptRequest."""
    request = PromptRequest(
        user_id=1,
        topic="Testing",
        learning_style=learning_style,
        difficulty="Intermediate"
    )
    result = ConsensusResult(
        request_id=42,
        final_prompt=prompt,
        quality_score=0.0
    )
    result.request = request
    return result


def test_empty_prompt_validation():
    """Verify that PromptScoringError is raised when final prompt is empty or whitespace."""
    scorer = PromptScorer()

    # Empty string
    res_empty = create_mock_consensus("")
    with pytest.raises(PromptScoringError, match="cannot be empty"):
        scorer.score_prompt(res_empty)

    # Whitespace only
    res_space = create_mock_consensus("   \n  \t ")
    with pytest.raises(PromptScoringError, match="cannot be empty"):
        scorer.score_prompt(res_space)

    # Calling individual methods directly
    with pytest.raises(PromptScoringError, match="cannot be empty"):
        scorer.score_clarity("  ")


def test_none_prompt_validation():
    """Verify that PromptScoringError is raised when prompt is None."""
    scorer = PromptScorer()

    # None prompt on consensus result
    res_none = create_mock_consensus(None)
    res_none.final_prompt = None
    with pytest.raises(PromptScoringError, match="cannot be None"):
        scorer.score_prompt(res_none)

    # Calling individual methods directly
    with pytest.raises(PromptScoringError, match="cannot be None"):
        scorer.score_structure(None)


def test_invalid_inputs():
    """Verify validation when consensus_result is None or has wrong type, or invalid style type."""
    scorer = PromptScorer()

    # None consensus result
    with pytest.raises(PromptScoringError, match="consensus_result cannot be None"):
        scorer.score_prompt(None)

    # Invalid type for consensus result
    with pytest.raises(PromptScoringError, match="must be a ConsensusResult instance"):
        scorer.score_prompt("Not a consensus result")

    # Invalid type for prompt inside helper validation
    with pytest.raises(PromptScoringError, match="must be a string"):
        scorer.score_clarity(12345)

    # Invalid learning style type
    res = create_mock_consensus("This is a valid prompt.")
    with pytest.raises(PromptScoringError, match="must be a string or None"):
        scorer.score_prompt(res, learning_style=123)

    # Unsupported learning style string
    with pytest.raises(PromptScoringError, match="Unsupported learning style"):
        scorer.score_prompt(res, learning_style="invalid_style")


def test_short_prompt_scoring():
    """Verify that short prompts receive relatively low scores on structure and depth."""
    scorer = PromptScorer()
    res = create_mock_consensus("Define photosynthesis.")

    score = scorer.score_prompt(res, learning_style="visual")

    assert score.depth < 10.0
    assert score.structure < 10.0
    assert score.overall_score < 50.0


def test_long_prompt_scoring():
    """Verify that longer prompts containing descriptive detail receive higher depth scores."""
    scorer = PromptScorer()

    short_prompt = "Explain cellular respiration."
    long_prompt = (
        "Explain cellular respiration in detail. Focus on the glycolysis process, the Krebs cycle, "
        "and the electron transport chain. Detail the ATP yield at each phase. Explain the underlying "
        "chemical reactions, cause and effect of oxygen presence, and cellular mechanisms. "
        "Ensure we cover the theory and principles of metabolic pathways, framework, and conceptual synthesis. "
        "This long explanation provides extensive supporting context and detail for the biology concepts."
    )

    res_short = create_mock_consensus(short_prompt)
    res_long = create_mock_consensus(long_prompt)

    score_short = scorer.score_prompt(res_short)
    score_long = scorer.score_prompt(res_long)

    assert score_long.depth > score_short.depth
    assert score_long.depth >= 12.0


def test_educational_prompt_scoring():
    """Verify that prompts designed with pedagogy (examples, outcomes, active tasks) score high on effectiveness."""
    scorer = PromptScorer()

    plain_prompt = "Tell me about gravity."
    educational_prompt = (
        "Objective: The learner will understand gravity. "
        "For instance, consider how an apple falls to the ground. "
        "Let's compare this to orbital motion. Explain the difference. "
        "Now solve this practice problem: calculate the force if mass is doubled. "
        "Reflect on this question: what would happen without gravity?"
    )

    res_plain = create_mock_consensus(plain_prompt)
    res_edu = create_mock_consensus(educational_prompt)

    score_plain = scorer.score_educational_effectiveness(res_plain.final_prompt)
    score_edu = scorer.score_educational_effectiveness(res_edu.final_prompt)

    assert score_edu > score_plain
    assert score_edu >= 15.0


def test_personalized_prompt_scoring():
    """Verify that personalization matches the target style keywords."""
    scorer = PromptScorer()

    prompt = "This conversational storytelling scenario helps you imagine and think about the dialogue."
    res = create_mock_consensus(prompt, learning_style="conversational")

    # High score for matched style
    score_matched = scorer.score_personalization(prompt, learning_style="conversational")
    # Lower score for mismatched style
    score_mismatched = scorer.score_personalization(prompt, learning_style="research_oriented")

    assert score_matched > score_mismatched


def test_visual_learner_prompt_scoring():
    """Verify that visual prompts containing headings, lists, and visual keywords score high for visual learners."""
    scorer = PromptScorer()

    visual_prompt = (
        "# Photosynthesis Process\n\n"
        "Here is a visual flowchart describing the system hierarchy:\n"
        "- Leaf captures sunlight (visual capture)\n"
        "- Stomata intake CO2 (illustrated process)\n"
        "This diagram outlines the spatial organization and relationship between variables."
    )

    # Scores high for visual
    score_visual = scorer.score_personalization(visual_prompt, learning_style="visual")
    # Penalized style or mismatched
    score_conv = scorer.score_personalization(visual_prompt, learning_style="conversational")

    assert score_visual >= 12.0
    assert score_visual > score_conv


def test_exam_focused_learner_prompt_scoring():
    """Verify that exam-focused prompts with practice quizzes/terms score high for exam style."""
    scorer = PromptScorer()

    exam_prompt = (
        "Key Concept: Photosynthesis.\n"
        "Recall high-yield definitions. Practice questions:\n"
        "1. What is the yield of photosynthesis?\n"
        "2. Explain why wrong answers are wrong."
    )

    score_exam = scorer.score_personalization(exam_prompt, learning_style="exam_focused")
    score_research = scorer.score_personalization(exam_prompt, learning_style="research_oriented")

    assert score_exam >= 12.0
    assert score_exam > score_research


def test_overall_score_calculation():
    """Verify that overall_score is the sum of category scores."""
    scorer = PromptScorer()
    prompt = (
        "# Photosynthesis Overview\n\n"
        "Objective: Understand the chemical process of photosynthesis.\n"
        "For example, plants use light energy to synthesize glucose. Explain how they compare.\n"
        "1. Capture light\n"
        "2. Convert energy\n"
        "Reflect on this: why is chlorophyll green?"
    )
    res = create_mock_consensus(prompt, learning_style="step_by_step")
    score = scorer.score_prompt(res)

    expected_sum = (
        score.clarity +
        score.structure +
        score.personalization +
        score.educational_effectiveness +
        score.depth
    )

    assert round(score.overall_score, 2) == round(expected_sum, 2)
    assert score.classification in ["Excellent", "Good", "Fair", "Poor"]


def test_serialization_compatibility():
    """Verify that the returned ResponseScore model is fully serialization-compatible."""
    scorer = PromptScorer()
    prompt = "Create a basic tutorial on loop loops. Explain the logic."
    res = create_mock_consensus(prompt)
    score = scorer.score_prompt(res)

    # Test dictionary conversion
    serialized = score.to_dict()
    assert isinstance(serialized, dict)
    assert "clarity" in serialized
    assert "overall_score" in serialized
    assert "classification" in serialized
    assert "notes" in serialized

    # Test json serialization
    json_str = json.dumps(serialized)
    assert isinstance(json_str, str)

    # Re-parse validation
    parsed = json.loads(json_str)
    assert parsed["clarity"] == score.clarity
    assert parsed["overall_score"] == score.overall_score


def test_score_ranges_between_0_and_20():
    """Verify that all category scores are bounded strictly between 0.0 and 20.0."""
    scorer = PromptScorer()

    # Extreme minimal prompt
    min_prompt = "A"
    res_min = create_mock_consensus(min_prompt)
    try:
        score_min = scorer.score_prompt(res_min)
        assert 0.0 <= score_min.clarity <= 20.0
        assert 0.0 <= score_min.structure <= 20.0
        assert 0.0 <= score_min.personalization <= 20.0
        assert 0.0 <= score_min.educational_effectiveness <= 20.0
        assert 0.0 <= score_min.depth <= 20.0
    except PromptScoringError:
        # If too short and rejected (e.g. if single character is considered empty/invalid)
        pass

    # High quality prompt
    max_prompt = (
        "# Comprehensive Photosynthesis Lesson\n\n"
        "Objective: The learner will detail the biochemical stages of photosynthesis.\n"
        "Introduction:\n"
        "Photosynthesis is a vital mechanism where light energy is converted to chemical energy. "
        "For example, let's look at the chloroplast diagram. Draw a flowchart of the electron transfer.\n\n"
        "Steps:\n"
        "1. Light-Dependent Reactions: Chlorophyll absorbs photons. This triggers water photolysis.\n"
        "2. Calvin Cycle: Carbon fixation occurs in the stroma. Sugar is synthesized.\n\n"
        "Pedagogical Guidance:\n"
        "Compare the raw inputs with the final products. Analyze the energy transformation. "
        "Reflect on how this supports life on Earth. Why is oxygen a byproduct?\n"
        "Practice Task:\n"
        "Explain the chemical equation in your own words. Check your understanding."
    )
    res_max = create_mock_consensus(max_prompt, learning_style="visual")
    score_max = scorer.score_prompt(res_max)

    for cat in ["clarity", "structure", "personalization", "educational_effectiveness", "depth"]:
        val = getattr(score_max, cat)
        assert 0.0 <= val <= 20.0


def test_overall_score_remains_between_0_and_100():
    """Verify that overall_score is bounded strictly between 0.0 and 100.0."""
    scorer = PromptScorer()
    prompt = "Simple test prompt."
    res = create_mock_consensus(prompt)
    score = scorer.score_prompt(res)

    assert 0.0 <= score.overall_score <= 100.0
