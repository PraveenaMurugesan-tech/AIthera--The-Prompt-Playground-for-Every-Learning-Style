import json
import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from scripts.benchmark_council import BenchmarkRunner, normalize_learning_style
from src.models.council_response import CouncilResponse
from src.models.consensus_result import ConsensusResult
from src.scoring.prompt_scorer import ResponseScore

@pytest.fixture
def temp_benchmark_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    
    prompts = [
        {
            "topic": "Python",
            "learning_style": "Step-by-step learner",
            "difficulty": "Beginner",
            "goal": "Learn loops"
        }
    ]
    
    data_path = data_dir / "benchmark_prompts.json"
    with open(data_path, "w") as f:
        json.dump(prompts, f)
        
    return str(data_path), str(reports_dir)

def test_benchmark_runner_loads_prompts(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    prompts = runner.load_prompts()
    assert len(prompts) == 1
    assert prompts[0]["topic"] == "Python"

import asyncio

def test_benchmark_runner_execution(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    # Mock the LiveCouncil execute method
    consensus_mock = MagicMock()
    consensus_mock.contributors = ["Groq", "Gemini"]
    consensus_mock.quality_score = 0.9
    consensus_mock.confidence_score = 95.0
    consensus_mock.agreement_score = 0.8
    consensus_mock.completeness_score = 90.0
    consensus_mock.learning_style_score = 100.0
    consensus_mock.provider_contributions = {"Groq": ["examples"], "Gemini": ["visuals"]}
    consensus_mock.diversity_score = 42.0
    consensus_mock.diversity_level = "Medium"
    consensus_mock.coverage_score = 80.0
    consensus_mock.learning_style_verification = {"requested": "Visual", "detected": "Visual", "confidence": 100}
    consensus_mock.explanation = "Groq won because X."
    consensus_mock.evaluation_summary = "High confidence consensus."
    consensus_mock.confidence_level = "High"
    consensus_mock.conflicting_concepts = []
    
    mock_result = {
        "responses": [
            MagicMock(provider_name="Gemini", model="Gemini", prompt="Good", metadata=MagicMock(response_time=0.5)),
            MagicMock(provider_name="Groq", model="Groq", prompt="Fast", metadata=MagicMock(response_time=0.2))
        ],
        "consensus": consensus_mock,
        "score": MagicMock(overall_score=85, classification="GOOD"),
        "contributors": ["Gemini", "Groq"]
    }
    
    runner.council.execute = AsyncMock(return_value=mock_result)
    
    # Run the benchmark
    prompts = runner.load_prompts()
    asyncio.run(runner.run_single_benchmark(prompts[0], 1, 1))
    
    assert len(runner.results) == 1
    res = runner.results[0]
    
    assert res["topic"] == "Python"
    assert res["winning_provider"] == "Groq"
    assert res["prompt_score"] == 85
    assert res["consensus_score"] == 0.9
    assert res["num_successful_providers"] == 2
    
    # Check statistics
    stats = runner.compute_statistics()
    assert stats["total_runs"] == 1
    assert stats["successful_runs"] == 1
    assert stats["most_frequent_winner"] == "Groq"
    assert stats["fastest_provider"] == "Groq"
    
    # Check reports generation
    runner.generate_reports(stats)
    
    assert os.path.exists(os.path.join(reports_dir, "benchmark_results.json"))
    assert os.path.exists(os.path.join(reports_dir, "benchmark_results.csv"))
    assert os.path.exists(os.path.join(reports_dir, "benchmark_summary.md"))

def test_benchmark_runner_provider_identity(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    # Mock the LiveCouncil execute method with two providers sharing the same model
    consensus_mock = MagicMock()
    consensus_mock.contributors = ["Cerebras", "OpenRouter"]
    consensus_mock.quality_score = 0.9
    consensus_mock.confidence_score = 90.0
    consensus_mock.agreement_score = 0.8
    consensus_mock.completeness_score = 90.0
    consensus_mock.learning_style_score = 100.0
    consensus_mock.provider_contributions = {"Cerebras": ["structure"]}
    consensus_mock.diversity_score = 42.0
    consensus_mock.diversity_level = "Medium"
    consensus_mock.coverage_score = 80.0
    consensus_mock.learning_style_verification = {"requested": "Visual", "detected": "Visual", "confidence": 100}
    consensus_mock.explanation = "Groq won because X."
    consensus_mock.evaluation_summary = "High confidence consensus."
    consensus_mock.confidence_level = "High"
    consensus_mock.conflicting_concepts = []
    
    mock_result = {
        "responses": [
            MagicMock(provider_name="Cerebras", model="gpt-oss-120b", prompt="Good", metadata=MagicMock(response_time=0.5)),
            MagicMock(provider_name="OpenRouter", model="gpt-oss-120b", prompt="Fast", metadata=MagicMock(response_time=0.2))
        ],
        "consensus": consensus_mock,
        "score": MagicMock(overall_score=85, classification="GOOD"),
        "contributors": ["Cerebras", "OpenRouter"],
        "failed_providers": ["Groq"],
        "error_details": {}
    }
    
    runner.council.execute = AsyncMock(return_value=mock_result)
    
    # Run the benchmark
    prompts = runner.load_prompts()
    asyncio.run(runner.run_single_benchmark(prompts[0], 1, 1))
    
    assert len(runner.results) == 1
    res = runner.results[0]
    
    # Ensure they are separate in provider_stats
    assert len(res["provider_stats"]) == 3
    assert res["num_successful_providers"] == 2
    
    cerebras_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "Cerebras")
    assert cerebras_stat["model_name"] == "gpt-oss-120b"
    
    openrouter_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "OpenRouter")
    assert openrouter_stat["model_name"] == "gpt-oss-120b"
    
    # Ensure statistics are aggregated separately
    stats = runner.compute_statistics()
    assert stats["provider_success_rates"]["Cerebras"] == 100.0
    assert stats["provider_success_rates"]["OpenRouter"] == 100.0

def test_benchmark_runner_handles_failures(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    # Mock to throw exception
    runner.council.execute = AsyncMock(side_effect=Exception("API failure"))
    
    prompts = runner.load_prompts()
    asyncio.run(runner.run_single_benchmark(prompts[0], 1, 1))
    
    assert len(runner.results) == 1
    res = runner.results[0]
    assert res["winning_provider"] == "error"
    assert res["error"] == "API failure"
    assert res["prompt_score"] == 0.0
    
    stats = runner.compute_statistics()
    assert stats["error"] == "All runs failed"

def test_benchmark_runner_handles_provider_errors(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    consensus_mock = MagicMock()
    consensus_mock.contributors = ["Gemini"]
    consensus_mock.quality_score = 0.9
    consensus_mock.agreement_score = 0.8
    consensus_mock.diversity_score = 42.0
    consensus_mock.diversity_level = "Medium"
    consensus_mock.coverage_score = 80.0
    consensus_mock.learning_style_verification = {"requested": "Visual", "detected": "Visual", "confidence": 100}
    consensus_mock.explanation = "Groq won because X."
    consensus_mock.evaluation_summary = "High confidence consensus."
    consensus_mock.confidence_level = "High"
    consensus_mock.conflicting_concepts = []
    consensus_mock.provider_contributions = {}
    consensus_mock.learning_style_score = 100.0
    consensus_mock.completeness_score = 90.0

    mock_result = {
        "responses": [
            MagicMock(provider_name="Gemini", model="Gemini", prompt="Good", metadata=MagicMock(response_time=0.5)),
        ],
        "consensus": consensus_mock,
        "score": MagicMock(overall_score=85, classification="GOOD"),
        "contributors": ["Gemini"],
        "failed_providers": ["Claude", "DeepSeek", "SambaNova", "Cerebras"],
        "error_details": {
            "Claude": {"type": "ClaudeAPIStatusError", "status_code": 400, "message": "Credit balance too low"},
            "DeepSeek": {"type": "DeepSeekAPIStatusError", "status_code": 402, "message": "Insufficient balance"},
            "SambaNova": {"type": "SambaNovaRateLimitError", "status_code": 429, "message": "Rate limit exceeded"},
            "Cerebras": "Unknown error"
        }
    }
    
    runner.council.execute = AsyncMock(return_value=mock_result)
    
    prompts = runner.load_prompts()
    asyncio.run(runner.run_single_benchmark(prompts[0], 1, 1))
    
    assert len(runner.results) == 1
    res = runner.results[0]
    
    # 1 success + 4 failures = 5 stats
    assert len(res["provider_stats"]) == 5
    
    claude_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "Claude")
    assert not claude_stat["success"]
    assert "400 ClaudeAPIStatusError: Credit balance too low" in claude_stat["error_message"]
    
    deepseek_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "DeepSeek")
    assert "402 DeepSeekAPIStatusError: Insufficient balance" in deepseek_stat["error_message"]
    
    samba_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "SambaNova")
    assert "429 SambaNovaRateLimitError: Rate limit exceeded" in samba_stat["error_message"]
    
    stats = runner.compute_statistics()
    # verify Attempts and successes
    assert stats["provider_success_rates"]["Claude"] == 0.0
    assert stats["provider_success_rates"]["DeepSeek"] == 0.0
    assert stats["provider_success_rates"]["SambaNova"] == 0.0
    assert stats["provider_success_rates"]["Gemini"] == 100.0

def test_benchmark_runner_handles_provider_timeout(temp_benchmark_dir):
    data_path, reports_dir = temp_benchmark_dir
    runner = BenchmarkRunner(data_path, reports_dir)
    
    consensus_mock = MagicMock()
    consensus_mock.contributors = ["Groq", "Gemini"]
    consensus_mock.quality_score = 0.9
    consensus_mock.agreement_score = 0.8
    consensus_mock.diversity_score = 42.0
    consensus_mock.diversity_level = "Medium"
    consensus_mock.coverage_score = 80.0
    consensus_mock.learning_style_verification = {"requested": "Visual", "detected": "Visual", "confidence": 100}
    consensus_mock.explanation = "Groq won because X."
    consensus_mock.evaluation_summary = "High confidence consensus."
    consensus_mock.confidence_level = "High"
    consensus_mock.conflicting_concepts = []
    consensus_mock.provider_contributions = {}
    consensus_mock.learning_style_score = 100.0
    consensus_mock.completeness_score = 90.0

    mock_result = {
        "responses": [
            MagicMock(provider_name="Groq", model="Groq", prompt="Good", metadata=MagicMock(response_time=0.5)),
            MagicMock(provider_name="Gemini", model="Gemini", prompt="Okay", metadata=MagicMock(response_time=0.6))
        ],
        "consensus": consensus_mock,
        "score": MagicMock(overall_score=85, classification="GOOD"),
        "contributors": ["Groq", "Gemini"],
        "failed_providers": ["OpenRouter"],
        "error_details": {
            "OpenRouter": {"type": "TimeoutError", "status_code": "N/A", "message": "TimeoutError"}
        }
    }
    
    runner.council.execute = AsyncMock(return_value=mock_result)
    
    prompts = runner.load_prompts()
    asyncio.run(runner.run_single_benchmark(prompts[0], 1, 1))
    
    assert len(runner.results) == 1
    res = runner.results[0]
    
    assert len(res["provider_stats"]) == 3
    
    openrouter_stat = next(p for p in res["provider_stats"] if p["provider_name"] == "OpenRouter")
    assert not openrouter_stat["success"]
    assert "TimeoutError" in openrouter_stat["error_message"]
    
    stats = runner.compute_statistics()
    assert stats["provider_success_rates"]["OpenRouter"] == 0.0
    assert stats["provider_success_rates"]["Groq"] == 100.0
    assert stats["provider_success_rates"]["Gemini"] == 100.0

def test_normalize_learning_style_mappings():
    # Valid mapping tests
    assert normalize_learning_style("Visual learner") == "visual"
    assert normalize_learning_style("Step-by-step learner") == "step_by_step"
    assert normalize_learning_style("Hands-on learner") == "step_by_step"
    assert normalize_learning_style("Project-based learning") == "step_by_step"
    assert normalize_learning_style("Exam preparation") == "exam_focused"
    assert normalize_learning_style("Beginner learner") == "conversational"
    assert normalize_learning_style("Advanced learner") == "research_oriented"

def test_normalize_learning_style_already_valid():
    # Already valid enum values
    assert normalize_learning_style("visual") == "visual"
    assert normalize_learning_style("conversational") == "conversational"
    assert normalize_learning_style("step_by_step") == "step_by_step"
    assert normalize_learning_style("exam_focused") == "exam_focused"
    assert normalize_learning_style("research_oriented") == "research_oriented"

def test_normalize_learning_style_case_insensitive():
    # Case insensitivity and whitespace
    assert normalize_learning_style("  ViSuAl LeArNeR  ") == "visual"
    assert normalize_learning_style("STEP-BY-STEP LEARNER") == "step_by_step"

def test_normalize_learning_style_invalid():
    # Invalid values raise ValueError
    with pytest.raises(ValueError, match="Unknown learning style: 'Invalid style'"):
        normalize_learning_style("Invalid style")
