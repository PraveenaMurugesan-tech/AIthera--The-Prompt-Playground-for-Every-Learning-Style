import pytest
from unittest.mock import patch, AsyncMock
from pathlib import Path

from src.council.council_executor import CouncilExecutor, CouncilExecutionResult, CouncilExecutionError
from src.models.user import User
from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse, CouncilResponseDB
from src.models.consensus_result import ConsensusResult
from src.models.explanation import Explanation

# AnyIO test marker to allow async tests
pytestmark = pytest.mark.anyio

# ==============================================================================
# Mock Responses
# ==============================================================================

MOCK_GROQ_DICT = {
    "choices": [
        {
            "message": {
                "content": '{"prompt": "Groq visual prompt", "reasoning": "Groq visual reasoning", "strengths": ["Visual layout"]}'
            }
        }
    ],
    "usage": {"total_tokens": 100},
    "model": "llama-3.3-70b-versatile",
    "response_time": 0.5
}

MOCK_CLAUDE_DICT = {
    "content": [
        {
            "text": '{"prompt": "Claude conversational prompt", "reasoning": "Claude conversational reasoning", "strengths": ["Storytelling"]}'
        }
    ],
    "usage": {"input_tokens": 50, "output_tokens": 50},
    "model": "claude-3-5-sonnet",
    "response_time": 0.6
}

MOCK_GEMINI_DICT = {
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": '{"prompt": "Gemini visual prompt", "reasoning": "Gemini visual reasoning", "strengths": ["Diagrams"]}'
                    }
                ]
            }
        }
    ],
    "usageMetadata": {"totalTokenCount": 120},
    "modelVersion": "gemini-1.5-pro",
    "response_time": 0.4
}

MOCK_DEEPSEEK_DICT = {
    "choices": [
        {
            "message": {
                "content": '{"prompt": "DeepSeek logic prompt", "reasoning": "DeepSeek logic reasoning", "strengths": ["Logical steps"]}'
            }
        }
    ],
    "usage": {"total_tokens": 90},
    "model": "deepseek-chat",
    "response_time": 0.7
}

MOCK_OPENROUTER_DICT = {
    "choices": [
        {
            "message": {
                "content": '{"prompt": "OpenRouter teacher prompt", "reasoning": "OpenRouter reasoning", "strengths": ["Teaching steps"]}'
            }
        }
    ],
    "usage": {"total_tokens": 80},
    "model": "openai/gpt-oss-120b",
    "response_time": 0.3
}

MOCK_CEREBRAS_DICT = {
    "choices": [
        {
            "message": {
                "content": '{"prompt": "Cerebras prompt", "reasoning": "Cerebras reasoning", "strengths": ["Speed"]}'
            }
        }
    ],
    "usage": {"total_tokens": 70},
    "model": "llama-4-scout-17b-16e-instruct",
    "response_time": 0.2
}

MOCK_SAMBANOVA_DICT = {
    "choices": [
        {
            "message": {
                "content": '{"prompt": "SambaNova prompt", "reasoning": "SambaNova reasoning", "strengths": ["Analysis"]}'
            }
        }
    ],
    "usage": {"total_tokens": 100},
    "model": "Meta-Llama-3.3-70B-Instruct",
    "response_time": 0.5
}

# ==============================================================================
# Unit Tests
# ==============================================================================

def test_template_loading():
    """Verify loading templates and error handling for missing templates."""
    executor = CouncilExecutor()
    
    # Load existing template
    content = executor.load_template("gpt_teacher.txt")
    assert isinstance(content, str)
    assert "{topic}" in content
    
    # Raising error on missing template
    with pytest.raises(CouncilExecutionError, match="Template file not found"):
        executor.load_template("non_existent_template.txt")


def test_variable_substitution():
    """Verify variables are injected correctly and errors are raised for invalid inputs."""
    executor = CouncilExecutor()
    template = "Topic: {topic}, Objective: {objective}, Style: {learning_style}, Diff: {difficulty}, Edu: {education_level}, Len: {output_length}"
    
    result = executor.substitute_template_variables(
        template=template,
        topic="Math",
        objective="Learn fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    assert result == "Topic: Math, Objective: Learn fractions, Style: visual, Diff: beginner, Edu: elementary, Len: short"

    # Empty variable raising CouncilExecutionError
    with pytest.raises(CouncilExecutionError, match="Template variable 'topic' is empty or None"):
        executor.substitute_template_variables(
            template=template,
            topic="",
            objective="Learn fractions",
            learning_style="visual",
            difficulty="beginner",
            education_level="elementary",
            output_length="short"
        )

    # Missing variable raising CouncilExecutionError
    bad_template = "Topic: {topic} and {missing_var}"
    with pytest.raises(CouncilExecutionError, match="Missing template variable"):
        executor.substitute_template_variables(
            template=bad_template,
            topic="Math",
            objective="Learn fractions",
            learning_style="visual",
            difficulty="beginner",
            education_level="elementary",
            output_length="short"
        )


def test_build_provider_prompt():
    """Verify provider specific prompts are correctly built."""
    executor = CouncilExecutor()
    prompt = executor.build_provider_prompt(
        provider_name="groq",
        topic="Physics",
        objective="Learn gravity",
        learning_style="visual",
        difficulty="intermediate",
        education_level="high_school",
        output_length="moderate"
    )
    assert isinstance(prompt, str)
    assert "Physics" in prompt

    # Unknown provider raising CouncilExecutionError
    with pytest.raises(CouncilExecutionError, match="Unknown provider"):
        executor.build_provider_prompt(
            provider_name="invalid_provider",
            topic="Physics",
            objective="Learn gravity",
            learning_style="visual",
            difficulty="intermediate",
            education_level="high_school",
            output_length="moderate"
        )


def test_validation():
    """Verify PromptRequest validation and learning style validation."""
    executor = CouncilExecutor()
    
    # Missing topic
    bad_request = PromptRequest(
        user_id=1,
        topic="",
        objective="Learn fractions",
        learning_style="visual",
        difficulty="beginner",
        education_level="elementary",
        output_length="short"
    )
    with pytest.raises(CouncilExecutionError, match="PromptRequest must have topic and objective"):
        executor._validate_request(bad_request)

    # Invalid learning style
    with pytest.raises(CouncilExecutionError, match="Invalid learning style"):
        executor._validate_learning_style("kinesthetic")


@patch("src.council.council_executor.SambaNovaClient")
@patch("src.council.council_executor.GroqClient")
@patch("src.council.council_executor.ClaudeClient")
@patch("src.council.council_executor.GeminiClient")
@patch("src.council.council_executor.DeepSeekClient")
@patch("src.council.council_executor.OpenRouterClient")
@patch("src.council.council_executor.CerebrasClient")
async def test_execute_success(
    mock_cerebras_class, mock_openrouter_class, mock_deepseek_class, mock_gemini_class, mock_claude_class, mock_groq_class, mock_sambanova_class
):
    """Verify success flow where all providers succeed and results are normalized."""
    # Setup mock instances and generate_response return values
    mock_groq = mock_groq_class.return_value
    mock_groq.generate_response = AsyncMock(return_value=MOCK_GROQ_DICT)
    mock_groq.get_role.return_value = "creator"

    mock_claude = mock_claude_class.return_value
    mock_claude.generate_response = AsyncMock(return_value=MOCK_CLAUDE_DICT)
    mock_claude.get_role.return_value = "validator"

    mock_gemini = mock_gemini_class.return_value
    mock_gemini.generate_response = AsyncMock(return_value=MOCK_GEMINI_DICT)
    mock_gemini.get_role.return_value = "refiner"

    mock_deepseek = mock_deepseek_class.return_value
    mock_deepseek.generate_response = AsyncMock(return_value=MOCK_DEEPSEEK_DICT)
    mock_deepseek.get_role.return_value = "critic"

    mock_openrouter = mock_openrouter_class.return_value
    mock_openrouter.generate_response = AsyncMock(return_value=MOCK_OPENROUTER_DICT)
    mock_openrouter.get_role.return_value = "creator"

    mock_cerebras = mock_cerebras_class.return_value
    mock_cerebras.generate_response = AsyncMock(return_value=MOCK_CEREBRAS_DICT)
    mock_cerebras.get_role.return_value = "creator"

    mock_sambanova = mock_sambanova_class.return_value
    mock_sambanova.generate_response = AsyncMock(return_value=MOCK_SAMBANOVA_DICT)
    mock_sambanova.get_role.return_value = "creator"

    executor = CouncilExecutor()
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand the light reactions",
        learning_style="visual",
        difficulty="intermediate",
        education_level="high_school",
        output_length="moderate"
    )
    
    result = await executor.execute(request)
    
    # Assert structure and metrics
    assert isinstance(result, CouncilExecutionResult)
    assert len(result.responses) == 7
    assert len(result.successful_providers) == 7
    assert len(result.failed_providers) == 0
    assert result.execution_time > 0.0
    
    for name in ["Groq", "Claude", "Gemini", "DeepSeek", "OpenRouter", "Cerebras", "SambaNova"]:
        assert name in result.successful_providers

    # Assert normalized values
    for response in result.responses:
        assert isinstance(response, CouncilResponse)
        assert response.prompt is not None
        assert response.reasoning is not None
        assert len(response.strengths) > 0
        assert response.metadata.tokens_used > 0
        assert response.metadata.response_time > 0


@patch("src.council.council_executor.SambaNovaClient")
@patch("src.council.council_executor.GroqClient")
@patch("src.council.council_executor.ClaudeClient")
@patch("src.council.council_executor.GeminiClient")
@patch("src.council.council_executor.DeepSeekClient")
@patch("src.council.council_executor.OpenRouterClient")
@patch("src.council.council_executor.CerebrasClient")
async def test_execute_partial_failures(
    mock_cerebras_class, mock_openrouter_class, mock_deepseek_class, mock_gemini_class, mock_claude_class, mock_groq_class, mock_sambanova_class
):
    """Verify executor succeeds partially and logs failures when some providers fail."""
    mock_groq = mock_groq_class.return_value
    mock_groq.generate_response = AsyncMock(return_value=MOCK_GROQ_DICT)
    mock_groq.get_role.return_value = "creator"

    # Claude fails with exception
    mock_claude = mock_claude_class.return_value
    mock_claude.generate_response = AsyncMock(side_effect=Exception("Claude API offline"))
    mock_claude.get_role.return_value = "validator"

    # Gemini succeeds
    mock_gemini = mock_gemini_class.return_value
    mock_gemini.generate_response = AsyncMock(return_value=MOCK_GEMINI_DICT)
    mock_gemini.get_role.return_value = "refiner"

    # DeepSeek returns None
    mock_deepseek = mock_deepseek_class.return_value
    mock_deepseek.generate_response = AsyncMock(return_value=None)
    mock_deepseek.get_role.return_value = "critic"

    # OpenRouter succeeds
    mock_openrouter = mock_openrouter_class.return_value
    mock_openrouter.generate_response = AsyncMock(return_value=MOCK_OPENROUTER_DICT)
    mock_openrouter.get_role.return_value = "creator"

    # Cerebras succeeds
    mock_cerebras = mock_cerebras_class.return_value
    mock_cerebras.generate_response = AsyncMock(return_value=MOCK_CEREBRAS_DICT)
    mock_cerebras.get_role.return_value = "creator"

    # SambaNova succeeds
    mock_sambanova = mock_sambanova_class.return_value
    mock_sambanova.generate_response = AsyncMock(return_value=MOCK_SAMBANOVA_DICT)
    mock_sambanova.get_role.return_value = "creator"

    executor = CouncilExecutor()
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand the light reactions",
        learning_style="visual",
        difficulty="intermediate",
        education_level="high_school",
        output_length="moderate"
    )

    result = await executor.execute(request)

    assert isinstance(result, CouncilExecutionResult)
    assert len(result.responses) == 5  # Groq, Gemini, OpenRouter, Cerebras, SambaNova
    assert len(result.successful_providers) == 5
    assert len(result.failed_providers) == 2
    
    assert "Groq" in result.successful_providers
    assert "Gemini" in result.successful_providers
    assert "OpenRouter" in result.successful_providers
    assert "Cerebras" in result.successful_providers
    assert "SambaNova" in result.successful_providers
    
    assert "Claude" in result.failed_providers
    assert "DeepSeek" in result.failed_providers
    
    assert "Claude API offline" in result.error_details["Claude"]["message"]
    assert "Provider returned None" in result.error_details["DeepSeek"]["message"]


@patch("src.council.council_executor.SambaNovaClient")
@patch("src.council.council_executor.GroqClient")
@patch("src.council.council_executor.ClaudeClient")
@patch("src.council.council_executor.GeminiClient")
@patch("src.council.council_executor.DeepSeekClient")
@patch("src.council.council_executor.OpenRouterClient")
@patch("src.council.council_executor.CerebrasClient")
async def test_execute_normalization_failure(
    mock_cerebras_class, mock_openrouter_class, mock_deepseek_class, mock_gemini_class, mock_claude_class, mock_groq_class, mock_sambanova_class
):
    """Verify normalization failures are caught, logged, and executor continues."""
    mock_groq = mock_groq_class.return_value
    mock_groq.generate_response = AsyncMock(return_value=MOCK_GROQ_DICT)
    mock_groq.get_role.return_value = "creator"

    # Claude returns a malformed response dict
    mock_claude = mock_claude_class.return_value
    mock_claude.generate_response = AsyncMock(return_value={"malformed_response": "data"})
    mock_claude.get_role.return_value = "validator"

    mock_gemini = mock_gemini_class.return_value
    mock_gemini.generate_response = AsyncMock(return_value=MOCK_GEMINI_DICT)
    mock_gemini.get_role.return_value = "refiner"

    mock_deepseek = mock_deepseek_class.return_value
    mock_deepseek.generate_response = AsyncMock(return_value=MOCK_DEEPSEEK_DICT)
    mock_deepseek.get_role.return_value = "critic"

    mock_openrouter = mock_openrouter_class.return_value
    mock_openrouter.generate_response = AsyncMock(return_value=MOCK_OPENROUTER_DICT)
    mock_openrouter.get_role.return_value = "creator"

    mock_cerebras = mock_cerebras_class.return_value
    mock_cerebras.generate_response = AsyncMock(return_value=MOCK_CEREBRAS_DICT)
    mock_cerebras.get_role.return_value = "creator"

    mock_sambanova = mock_sambanova_class.return_value
    mock_sambanova.generate_response = AsyncMock(return_value=MOCK_SAMBANOVA_DICT)
    mock_sambanova.get_role.return_value = "creator"

    executor = CouncilExecutor()
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand the light reactions",
        learning_style="visual",
        difficulty="intermediate",
        education_level="high_school",
        output_length="moderate"
    )

    result = await executor.execute(request)

    assert isinstance(result, CouncilExecutionResult)
    assert len(result.responses) == 6  # Groq, Gemini, DeepSeek, OpenRouter, Cerebras, SambaNova
    assert "Claude" in result.failed_providers
    assert "Normalization failed" in result.error_details["Claude"]["message"]


@patch("src.council.council_executor.SambaNovaClient")
@patch("src.council.council_executor.GroqClient")
@patch("src.council.council_executor.ClaudeClient")
@patch("src.council.council_executor.GeminiClient")
@patch("src.council.council_executor.DeepSeekClient")
@patch("src.council.council_executor.OpenRouterClient")
@patch("src.council.council_executor.CerebrasClient")
async def test_execute_all_failures(
    mock_cerebras_class, mock_openrouter_class, mock_deepseek_class, mock_gemini_class, mock_claude_class, mock_groq_class, mock_sambanova_class
):
    """Verify that a CouncilExecutionError is raised if all providers fail."""
    mock_groq = mock_groq_class.return_value
    mock_groq.generate_response = AsyncMock(side_effect=Exception("Groq error"))
    mock_groq.get_role.return_value = "creator"

    mock_claude = mock_claude_class.return_value
    mock_claude.generate_response = AsyncMock(side_effect=Exception("Claude error"))
    mock_claude.get_role.return_value = "validator"

    mock_gemini = mock_gemini_class.return_value
    mock_gemini.generate_response = AsyncMock(side_effect=Exception("Gemini error"))
    mock_gemini.get_role.return_value = "refiner"

    mock_deepseek = mock_deepseek_class.return_value
    mock_deepseek.generate_response = AsyncMock(side_effect=Exception("DeepSeek error"))
    mock_deepseek.get_role.return_value = "critic"

    mock_openrouter = mock_openrouter_class.return_value
    mock_openrouter.generate_response = AsyncMock(side_effect=Exception("OpenRouter error"))
    mock_openrouter.get_role.return_value = "creator"

    mock_cerebras = mock_cerebras_class.return_value
    mock_cerebras.generate_response = AsyncMock(side_effect=Exception("Cerebras error"))
    mock_cerebras.get_role.return_value = "creator"

    mock_sambanova = mock_sambanova_class.return_value
    mock_sambanova.generate_response = AsyncMock(side_effect=Exception("SambaNova error"))
    mock_sambanova.get_role.return_value = "creator"

    executor = CouncilExecutor()
    request = PromptRequest(
        user_id=1,
        topic="Photosynthesis",
        objective="Understand the light reactions",
        learning_style="visual",
        difficulty="intermediate",
        education_level="high_school",
        output_length="moderate"
    )

    with pytest.raises(CouncilExecutionError, match="All providers failed"):
        await executor.execute(request)
