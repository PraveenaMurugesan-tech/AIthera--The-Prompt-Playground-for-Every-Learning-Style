"""
Tests for src.council.response_normalizer

Covers:
- Per-provider normalization (OpenAI, Claude, Gemini, DeepSeek)
- JSON-formatted content and plain-text fallback parsing
- Individual helper methods (extract_prompt, extract_reasoning, extract_strengths, extract_metadata)
- Universal dispatcher (normalize)
- NormalizationError for unsupported providers and malformed responses
- Edge cases (markdown code fences, missing fields, empty strengths)
"""

import json
import pytest
from src.council.response_normalizer import ResponseNormalizer, NormalizationError
from src.models.council_response import CouncilResponse, ResponseMetadata, ResponseScore


# ==============================================================================
# Mock Response Factories
# ==============================================================================

def _json_content(prompt: str, reasoning: str, strengths: list[str]) -> str:
    """Build a JSON-encoded content string for mock responses."""
    return json.dumps({
        "prompt": prompt,
        "reasoning": reasoning,
        "strengths": strengths,
    })


def make_openai_response(
    content: str = "",
    model: str = "gpt-4o-2024-05-13",
    total_tokens: int = 750,
    response_time: float = 1.23,
) -> dict:
    """Create a mock OpenAI Chat Completions API response."""
    if not content:
        content = _json_content(
            prompt="Explain photosynthesis using visual diagrams and flowcharts.",
            reasoning="Visual learners benefit from diagrammatic representations.",
            strengths=[
                "Strong visual metaphors",
                "Clear step-by-step flow",
                "Engaging diagram descriptions",
            ],
        )
    return {
        "id": "chatcmpl-test-001",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 200,
            "completion_tokens": 550,
            "total_tokens": total_tokens,
        },
        "response_time": response_time,
    }


def make_claude_response(
    content: str = "",
    model: str = "claude-3-5-sonnet-20241022",
    input_tokens: int = 180,
    output_tokens: int = 620,
    response_time: float = 1.87,
) -> dict:
    """Create a mock Anthropic Messages API response."""
    if not content:
        content = _json_content(
            prompt="Validate the photosynthesis lesson for pedagogical accuracy and completeness.",
            reasoning="Cross-referencing biological processes with learning objective alignment.",
            strengths=[
                "Thorough fact-checking",
                "Alignment with learning objectives",
                "Comprehensive coverage",
            ],
        )
    return {
        "id": "msg-test-001",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": content}],
        "stop_reason": "end_turn",
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        "response_time": response_time,
    }


def make_gemini_response(
    content: str = "",
    model_role: str = "model",
    total_token_count: int = 820,
    response_time: float = 0.95,
) -> dict:
    """Create a mock Google Gemini generateContent API response."""
    if not content:
        content = _json_content(
            prompt="Refine the photosynthesis lesson to increase engagement and interactivity.",
            reasoning="Added interactive quiz checkpoints between concept sections.",
            strengths=[
                "Interactive learning checkpoints",
                "Improved concept sequencing",
                "Better visual scaffold",
            ],
        )
    return {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": content}],
                    "role": model_role,
                },
                "finishReason": "STOP",
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 210,
            "candidatesTokenCount": 610,
            "totalTokenCount": total_token_count,
        },
        "response_time": response_time,
    }


def make_deepseek_response(
    content: str = "",
    model: str = "deepseek-chat",
    total_tokens: int = 690,
    response_time: float = 2.05,
) -> dict:
    """Create a mock DeepSeek Chat Completions API response (OpenAI-compatible)."""
    if not content:
        content = _json_content(
            prompt="Critique the photosynthesis lesson for depth and conceptual gaps.",
            reasoning="Identified gaps in light-dependent vs light-independent reactions coverage.",
            strengths=[
                "Identifies conceptual gaps",
                "Suggests depth improvements",
                "References curriculum standards",
            ],
        )
    return {
        "id": "chatcmpl-ds-test-001",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 190,
            "completion_tokens": 500,
            "total_tokens": total_tokens,
        },
        "response_time": response_time,
    }


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def normalizer() -> ResponseNormalizer:
    """Provide a fresh ResponseNormalizer instance."""
    return ResponseNormalizer()


# ==============================================================================
# Test: OpenAI Normalization
# ==============================================================================

class TestOpenAINormalization:
    """Tests for OpenAI provider normalization."""

    def test_normalize_openai_json_content(self, normalizer: ResponseNormalizer):
        """Structured JSON response produces a valid CouncilResponse."""
        raw = make_openai_response()
        result = normalizer.normalize_openai_response(raw)

        assert isinstance(result, CouncilResponse)
        assert result.model == "gpt-4o-2024-05-13"
        assert result.role == "creator"
        assert "photosynthesis" in result.prompt.lower()
        assert len(result.strengths) == 3
        assert result.metadata.tokens_used == 750
        assert result.metadata.response_time == 1.23
        assert result.metadata.provider_version == "gpt-4o-2024-05-13"

    def test_normalize_openai_custom_role(self, normalizer: ResponseNormalizer):
        """Custom role overrides the default."""
        raw = make_openai_response()
        result = normalizer.normalize_openai_response(raw, role="reviewer")
        assert result.role == "reviewer"

    def test_normalize_openai_plain_text_fallback(self, normalizer: ResponseNormalizer):
        """Plain text with Reasoning:/Strengths: labels parses correctly."""
        plain_text = (
            "Design a hands-on lab simulation for photosynthesis.\n"
            "Reasoning: Kinesthetic learners need physical interaction.\n"
            "Strengths:\n"
            "- Tactile engagement\n"
            "- Active experimentation\n"
        )
        raw = make_openai_response(content=plain_text)
        result = normalizer.normalize_openai_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "lab simulation" in result.prompt.lower()
        assert "kinesthetic" in result.reasoning.lower()
        assert len(result.strengths) >= 2

    def test_normalize_openai_markdown_code_fence(self, normalizer: ResponseNormalizer):
        """JSON wrapped in ```json fences is parsed correctly."""
        inner = _json_content(
            prompt="Teach GPT about photosynthesis with flowcharts",
            reasoning="Flowcharts map directly to visual processing",
            strengths=["Clear flow", "Visual mapping"],
        )
        fenced = f"```json\n{inner}\n```"
        raw = make_openai_response(content=fenced)
        result = normalizer.normalize_openai_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "flowcharts" in result.prompt.lower()

    def test_normalize_openai_malformed_structure(self, normalizer: ResponseNormalizer):
        """Missing 'choices' key raises NormalizationError."""
        raw = {"id": "chatcmpl-bad", "model": "gpt-4o"}
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_openai_response(raw)

    def test_normalize_openai_empty_choices(self, normalizer: ResponseNormalizer):
        """Empty choices list raises NormalizationError."""
        raw = {
            "choices": [],
            "model": "gpt-4o",
            "usage": {"total_tokens": 10},
        }
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_openai_response(raw)


# ==============================================================================
# Test: Claude Normalization
# ==============================================================================

class TestClaudeNormalization:
    """Tests for Claude provider normalization."""

    def test_normalize_claude_json_content(self, normalizer: ResponseNormalizer):
        """Structured JSON response produces a valid CouncilResponse."""
        raw = make_claude_response()
        result = normalizer.normalize_claude_response(raw)

        assert isinstance(result, CouncilResponse)
        assert result.model == "claude-3-5-sonnet-20241022"
        assert result.role == "validator"
        assert "validate" in result.prompt.lower()
        assert len(result.strengths) == 3
        # Claude token count = input + output
        assert result.metadata.tokens_used == 800
        assert result.metadata.response_time == 1.87

    def test_normalize_claude_custom_role(self, normalizer: ResponseNormalizer):
        """Custom role overrides the default."""
        raw = make_claude_response()
        result = normalizer.normalize_claude_response(raw, role="auditor")
        assert result.role == "auditor"

    def test_normalize_claude_plain_text(self, normalizer: ResponseNormalizer):
        """Plain text content with labels parses correctly."""
        plain = (
            "Audit the photosynthesis lesson structure.\n"
            "Reasoning: Verifying sequential concept flow is pedagogically sound.\n"
            "Strengths:\n"
            "- Logical flow\n"
            "- Concept dependency ordering\n"
        )
        raw = make_claude_response(content=plain)
        result = normalizer.normalize_claude_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "audit" in result.prompt.lower()
        assert len(result.strengths) >= 2

    def test_normalize_claude_string_content_item(self, normalizer: ResponseNormalizer):
        """Content item as a plain string (not a dict) is handled."""
        content = _json_content(
            prompt="Claude validates the quiz questions",
            reasoning="Each question maps to a learning objective",
            strengths=["Objective alignment"],
        )
        raw = make_claude_response()
        raw["content"] = [content]  # Plain string instead of {"type":"text","text":...}
        result = normalizer.normalize_claude_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "validates" in result.prompt.lower()

    def test_normalize_claude_malformed_no_content(self, normalizer: ResponseNormalizer):
        """Missing 'content' key raises NormalizationError."""
        raw = {"id": "msg-bad", "model": "claude-3-5-sonnet-20241022"}
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_claude_response(raw)

    def test_normalize_claude_no_usage(self, normalizer: ResponseNormalizer):
        """Missing 'usage' key returns None for tokens_used."""
        raw = make_claude_response()
        del raw["usage"]
        result = normalizer.normalize_claude_response(raw)

        assert result.metadata.tokens_used is None


# ==============================================================================
# Test: Gemini Normalization
# ==============================================================================

class TestGeminiNormalization:
    """Tests for Gemini provider normalization."""

    def test_normalize_gemini_json_content(self, normalizer: ResponseNormalizer):
        """Structured JSON response produces a valid CouncilResponse."""
        raw = make_gemini_response()
        result = normalizer.normalize_gemini_response(raw)

        assert isinstance(result, CouncilResponse)
        assert result.role == "refiner"
        assert "refine" in result.prompt.lower()
        assert len(result.strengths) == 3
        assert result.metadata.tokens_used == 820
        assert result.metadata.response_time == 0.95

    def test_normalize_gemini_custom_role(self, normalizer: ResponseNormalizer):
        """Custom role overrides the default."""
        raw = make_gemini_response()
        result = normalizer.normalize_gemini_response(raw, role="enhancer")
        assert result.role == "enhancer"

    def test_normalize_gemini_plain_text(self, normalizer: ResponseNormalizer):
        """Plain text content with labels parses correctly."""
        plain = (
            "Enhance the visual scaffolding of the lesson.\n"
            "Reasoning: Progressive disclosure improves comprehension.\n"
            "Strengths:\n"
            "- Better concept scaffolding\n"
            "- Progressive disclosure\n"
        )
        raw = make_gemini_response(content=plain)
        result = normalizer.normalize_gemini_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "enhance" in result.prompt.lower() or "scaffolding" in result.prompt.lower()

    def test_normalize_gemini_malformed_no_candidates(self, normalizer: ResponseNormalizer):
        """Missing 'candidates' key raises NormalizationError."""
        raw = {"usageMetadata": {"totalTokenCount": 100}}
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_gemini_response(raw)

    def test_normalize_gemini_empty_candidates(self, normalizer: ResponseNormalizer):
        """Empty candidates list raises NormalizationError."""
        raw = {
            "candidates": [],
            "usageMetadata": {"totalTokenCount": 100},
        }
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_gemini_response(raw)


# ==============================================================================
# Test: DeepSeek Normalization
# ==============================================================================

class TestDeepSeekNormalization:
    """Tests for DeepSeek provider normalization."""

    def test_normalize_deepseek_json_content(self, normalizer: ResponseNormalizer):
        """Structured JSON response produces a valid CouncilResponse."""
        raw = make_deepseek_response()
        result = normalizer.normalize_deepseek_response(raw)

        assert isinstance(result, CouncilResponse)
        assert result.model == "deepseek-chat"
        assert result.role == "critic"
        assert "critique" in result.prompt.lower()
        assert len(result.strengths) == 3
        assert result.metadata.tokens_used == 690
        assert result.metadata.response_time == 2.05
        assert result.metadata.provider_version == "deepseek-chat"

    def test_normalize_deepseek_custom_role(self, normalizer: ResponseNormalizer):
        """Custom role overrides the default."""
        raw = make_deepseek_response()
        result = normalizer.normalize_deepseek_response(raw, role="analyst")
        assert result.role == "analyst"

    def test_normalize_deepseek_plain_text(self, normalizer: ResponseNormalizer):
        """Plain text content with labels parses correctly."""
        plain = (
            "Identify missing topics in photosynthesis coverage.\n"
            "Reasoning: Curriculum mapping reveals uncovered light reactions.\n"
            "Strengths:\n"
            "- Gap analysis\n"
            "- Curriculum alignment\n"
            "- Depth evaluation\n"
        )
        raw = make_deepseek_response(content=plain)
        result = normalizer.normalize_deepseek_response(raw)

        assert isinstance(result, CouncilResponse)
        assert "missing topics" in result.prompt.lower() or "photosynthesis" in result.prompt.lower()
        assert len(result.strengths) >= 3

    def test_normalize_deepseek_malformed_structure(self, normalizer: ResponseNormalizer):
        """Missing 'choices' key raises NormalizationError."""
        raw = {"id": "ds-bad", "model": "deepseek-chat"}
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize_deepseek_response(raw)


# ==============================================================================
# Test: Universal Dispatcher
# ==============================================================================

class TestNormalizeDispatcher:
    """Tests for the universal normalize() dispatcher method."""

    @pytest.mark.parametrize(
        "provider_name, factory, expected_role",
        [
            ("openai", make_openai_response, "creator"),
            ("OpenAI", make_openai_response, "creator"),
            ("claude", make_claude_response, "validator"),
            ("Claude", make_claude_response, "validator"),
            ("gemini", make_gemini_response, "refiner"),
            ("Gemini", make_gemini_response, "refiner"),
            ("deepseek", make_deepseek_response, "critic"),
            ("DeepSeek", make_deepseek_response, "critic"),
        ],
    )
    def test_dispatch_all_providers(
        self, normalizer: ResponseNormalizer, provider_name: str, factory, expected_role: str
    ):
        """Dispatcher routes to the correct provider normalizer and assigns default role."""
        raw = factory()
        result = normalizer.normalize(provider_name, raw)

        assert isinstance(result, CouncilResponse)
        assert result.role == expected_role

    def test_dispatch_custom_role(self, normalizer: ResponseNormalizer):
        """Dispatcher passes a custom role through."""
        raw = make_openai_response()
        result = normalizer.normalize("openai", raw, role="orchestrator")
        assert result.role == "orchestrator"

    def test_dispatch_unsupported_provider(self, normalizer: ResponseNormalizer):
        """Unsupported provider raises NormalizationError."""
        raw = make_openai_response()
        with pytest.raises(NormalizationError, match="Unsupported AI provider"):
            normalizer.normalize("mistral", raw)

    def test_dispatch_non_dict_response(self, normalizer: ResponseNormalizer):
        """Non-dictionary response raises NormalizationError."""
        with pytest.raises(NormalizationError, match="must be a dictionary"):
            normalizer.normalize("openai", "this is a string, not a dict")

    def test_dispatch_none_response(self, normalizer: ResponseNormalizer):
        """None response raises NormalizationError."""
        with pytest.raises(NormalizationError, match="must be a dictionary"):
            normalizer.normalize("openai", None)

    def test_dispatch_list_response(self, normalizer: ResponseNormalizer):
        """List response raises NormalizationError."""
        with pytest.raises(NormalizationError, match="must be a dictionary"):
            normalizer.normalize("openai", [{"choices": []}])

    def test_dispatch_with_whitespace_provider(self, normalizer: ResponseNormalizer):
        """Provider name with leading/trailing whitespace is handled."""
        raw = make_claude_response()
        result = normalizer.normalize("  claude  ", raw)
        assert isinstance(result, CouncilResponse)
        assert result.role == "validator"


# ==============================================================================
# Test: Individual Helper Methods
# ==============================================================================

class TestExtractPrompt:
    """Tests for the extract_prompt() helper method."""

    def test_extract_prompt_openai(self, normalizer: ResponseNormalizer):
        raw = make_openai_response()
        prompt = normalizer.extract_prompt(raw, "openai")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "photosynthesis" in prompt.lower()

    def test_extract_prompt_claude(self, normalizer: ResponseNormalizer):
        raw = make_claude_response()
        prompt = normalizer.extract_prompt(raw, "claude")
        assert "validate" in prompt.lower()

    def test_extract_prompt_gemini(self, normalizer: ResponseNormalizer):
        raw = make_gemini_response()
        prompt = normalizer.extract_prompt(raw, "gemini")
        assert "refine" in prompt.lower()

    def test_extract_prompt_deepseek(self, normalizer: ResponseNormalizer):
        raw = make_deepseek_response()
        prompt = normalizer.extract_prompt(raw, "deepseek")
        assert "critique" in prompt.lower() or "photosynthesis" in prompt.lower()

    def test_extract_prompt_empty_content(self, normalizer: ResponseNormalizer):
        """Empty prompt content raises NormalizationError."""
        content = json.dumps({"prompt": "", "reasoning": "x", "strengths": ["a"]})
        raw = make_openai_response(content=content)
        with pytest.raises(NormalizationError, match="empty or invalid"):
            normalizer.extract_prompt(raw, "openai")

    def test_extract_prompt_whitespace_only(self, normalizer: ResponseNormalizer):
        """Whitespace-only prompt raises NormalizationError."""
        content = json.dumps({"prompt": "   ", "reasoning": "x", "strengths": ["a"]})
        raw = make_openai_response(content=content)
        with pytest.raises(NormalizationError, match="empty or invalid"):
            normalizer.extract_prompt(raw, "openai")


class TestExtractReasoning:
    """Tests for the extract_reasoning() helper method."""

    def test_extract_reasoning_openai(self, normalizer: ResponseNormalizer):
        raw = make_openai_response()
        reasoning = normalizer.extract_reasoning(raw, "openai")
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0

    def test_extract_reasoning_empty(self, normalizer: ResponseNormalizer):
        """Empty reasoning raises NormalizationError."""
        content = json.dumps({"prompt": "Valid prompt", "reasoning": "", "strengths": ["a"]})
        raw = make_openai_response(content=content)
        with pytest.raises(NormalizationError, match="empty or invalid"):
            normalizer.extract_reasoning(raw, "openai")


class TestExtractStrengths:
    """Tests for the extract_strengths() helper method."""

    def test_extract_strengths_openai(self, normalizer: ResponseNormalizer):
        raw = make_openai_response()
        strengths = normalizer.extract_strengths(raw, "openai")
        assert isinstance(strengths, list)
        assert len(strengths) == 3
        assert all(isinstance(s, str) for s in strengths)

    def test_extract_strengths_empty_list(self, normalizer: ResponseNormalizer):
        """Empty strengths list raises NormalizationError."""
        content = json.dumps({"prompt": "Valid", "reasoning": "Valid", "strengths": []})
        raw = make_openai_response(content=content)
        with pytest.raises(NormalizationError, match="empty or invalid"):
            normalizer.extract_strengths(raw, "openai")

    def test_extract_strengths_whitespace_entries(self, normalizer: ResponseNormalizer):
        """Strengths with only whitespace entries raises NormalizationError."""
        content = json.dumps({"prompt": "Valid", "reasoning": "Valid", "strengths": ["  ", ""]})
        raw = make_openai_response(content=content)
        with pytest.raises(NormalizationError, match="no valid strings"):
            normalizer.extract_strengths(raw, "openai")


class TestExtractMetadata:
    """Tests for the extract_metadata() helper method."""

    def test_extract_metadata_openai(self, normalizer: ResponseNormalizer):
        raw = make_openai_response()
        meta = normalizer.extract_metadata(raw, "openai")
        assert meta["tokens_used"] == 750
        assert meta["response_time"] == 1.23
        assert meta["provider_version"] == "gpt-4o-2024-05-13"

    def test_extract_metadata_claude(self, normalizer: ResponseNormalizer):
        raw = make_claude_response()
        meta = normalizer.extract_metadata(raw, "claude")
        assert meta["tokens_used"] == 800  # 180 + 620
        assert meta["response_time"] == 1.87
        assert meta["provider_version"] == "claude-3-5-sonnet-20241022"

    def test_extract_metadata_gemini(self, normalizer: ResponseNormalizer):
        raw = make_gemini_response()
        meta = normalizer.extract_metadata(raw, "gemini")
        assert meta["tokens_used"] == 820
        assert meta["response_time"] == 0.95

    def test_extract_metadata_deepseek(self, normalizer: ResponseNormalizer):
        raw = make_deepseek_response()
        meta = normalizer.extract_metadata(raw, "deepseek")
        assert meta["tokens_used"] == 690
        assert meta["response_time"] == 2.05
        assert meta["provider_version"] == "deepseek-chat"

    def test_extract_metadata_unsupported_provider(self, normalizer: ResponseNormalizer):
        """Unsupported provider raises NormalizationError."""
        with pytest.raises(NormalizationError, match="Unsupported provider"):
            normalizer.extract_metadata({}, "mistral")

    def test_extract_metadata_missing_usage(self, normalizer: ResponseNormalizer):
        """Missing usage field returns None for tokens_used."""
        raw = make_openai_response()
        del raw["usage"]
        meta = normalizer.extract_metadata(raw, "openai")
        assert meta["tokens_used"] is None

    def test_extract_metadata_missing_response_time(self, normalizer: ResponseNormalizer):
        """Missing response_time returns None."""
        raw = make_openai_response()
        del raw["response_time"]
        meta = normalizer.extract_metadata(raw, "openai")
        assert meta["response_time"] is None


# ==============================================================================
# Test: CouncilResponse Output Integrity
# ==============================================================================

class TestCouncilResponseIntegrity:
    """Validate that the normalized output is a well-formed CouncilResponse."""

    def test_output_has_all_fields(self, normalizer: ResponseNormalizer):
        """Normalized output contains all required CouncilResponse fields."""
        raw = make_openai_response()
        result = normalizer.normalize("openai", raw)

        assert hasattr(result, "model")
        assert hasattr(result, "role")
        assert hasattr(result, "prompt")
        assert hasattr(result, "reasoning")
        assert hasattr(result, "strengths")
        assert hasattr(result, "metadata")
        assert hasattr(result, "score")

    def test_output_metadata_type(self, normalizer: ResponseNormalizer):
        """Metadata is an instance of ResponseMetadata."""
        raw = make_claude_response()
        result = normalizer.normalize("claude", raw)
        assert isinstance(result.metadata, ResponseMetadata)

    def test_output_score_type(self, normalizer: ResponseNormalizer):
        """Score is an instance of ResponseScore with all None dimensions (uncalculated)."""
        raw = make_gemini_response()
        result = normalizer.normalize("gemini", raw)
        assert isinstance(result.score, ResponseScore)
        assert result.score.clarity is None
        assert result.score.structure is None
        # overall_score defaults to None (not yet calculated)
        assert result.score.overall_score is None or result.score.overall_score == 0.0

    def test_output_serializable(self, normalizer: ResponseNormalizer):
        """Normalized output is JSON-serializable via to_dict()."""
        raw = make_deepseek_response()
        result = normalizer.normalize("deepseek", raw)
        d = result.to_dict()
        assert isinstance(d, dict)
        serialized = json.dumps(d)
        assert isinstance(serialized, str)

    def test_calculate_overall_score_on_output(self, normalizer: ResponseNormalizer):
        """Score calculation works after normalization."""
        raw = make_openai_response()
        result = normalizer.normalize("openai", raw)

        result.score.clarity = 0.9
        result.score.structure = 0.85
        result.score.personalization = 0.80
        result.score.educational_effectiveness = 0.88
        result.score.depth = 0.75

        overall = result.calculate_overall_score()
        assert 0.0 <= overall <= 1.0
        assert result.score.overall_score == overall


# ==============================================================================
# Test: Edge Cases
# ==============================================================================

class TestEdgeCases:
    """Edge case scenarios for the normalizer."""

    def test_json_with_extra_fields_ignored(self, normalizer: ResponseNormalizer):
        """Extra fields in JSON content are ignored gracefully."""
        content = json.dumps({
            "prompt": "GPT generates a photosynthesis quiz.",
            "reasoning": "Quizzes reinforce retention.",
            "strengths": ["Active recall"],
            "extra_field": "should be ignored",
            "another": 42,
        })
        raw = make_openai_response(content=content)
        result = normalizer.normalize("openai", raw)
        assert isinstance(result, CouncilResponse)
        assert "quiz" in result.prompt.lower()

    def test_strengths_only_in_plain_text(self, normalizer: ResponseNormalizer):
        """Plain text with only Strengths: label (no Reasoning:) parses prompt and strengths."""
        plain = (
            "Build an interactive photosynthesis timeline.\n"
            "Strengths:\n"
            "- Chronological clarity\n"
            "- Visual timeline\n"
        )
        raw = make_openai_response(content=plain)
        result = normalizer.normalize("openai", raw)
        assert "timeline" in result.prompt.lower()
        assert len(result.strengths) >= 2

    def test_generic_code_fence_stripped(self, normalizer: ResponseNormalizer):
        """Generic ``` code fences (without language tag) are stripped."""
        inner = _json_content(
            prompt="GPT fenced response without json tag",
            reasoning="Testing fence stripping",
            strengths=["Fence removal"],
        )
        fenced = f"```\n{inner}\n```"
        raw = make_openai_response(content=fenced)
        result = normalizer.normalize("openai", raw)
        assert isinstance(result, CouncilResponse)
        assert "fenced" in result.prompt.lower()

    def test_claude_content_empty_list(self, normalizer: ResponseNormalizer):
        """Claude response with empty content list raises NormalizationError."""
        raw = make_claude_response()
        raw["content"] = []
        with pytest.raises(NormalizationError, match="Malformed raw response"):
            normalizer.normalize("claude", raw)

    def test_provider_name_case_insensitive(self, normalizer: ResponseNormalizer):
        """Provider name matching is case-insensitive."""
        raw = make_openai_response()
        result_lower = normalizer.normalize("openai", raw)
        result_upper = normalizer.normalize("OPENAI", raw)
        result_mixed = normalizer.normalize("OpenAI", raw)

        assert result_lower.role == result_upper.role == result_mixed.role == "creator"

    def test_provider_name_partial_match(self, normalizer: ResponseNormalizer):
        """Provider name with extra context still matches (e.g. 'openai-gpt4')."""
        raw = make_openai_response()
        result = normalizer.normalize("openai-gpt4", raw)
        assert isinstance(result, CouncilResponse)
