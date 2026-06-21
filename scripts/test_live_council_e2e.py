#!/usr/bin/env python3
"""
scripts/test_live_council_e2e.py - Phase 20.7

Real end-to-end integration test script verifying the AI Council workflow
using actual provider API keys from .env.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 output on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root is in path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.models.prompt_request import PromptRequest
from src.council.live_council import LiveCouncil, LiveCouncilError
from src.providers.provider_registry import ProviderRegistry
from src.providers.provider_health import ProviderHealthTracker


async def run_e2e():
    print("=================================")
    print("AI COUNCIL END-TO-END VALIDATION")
    print("=================================")

    # 1. Load environment variables
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print("✓ Loaded environment from .env")
    else:
        print("⚠️ .env file not found, reading from OS environment")

    # 2. Check and print configured providers
    providers = {
        "groq": "GROQ_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "claude": "CLAUDE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
    }

    configured_count = 0
    registry = ProviderRegistry()

    for name, env_var in providers.items():
        key_val = os.getenv(env_var)
        if key_val and key_val.strip():
            print(f"✓ {name.capitalize()} configured")
            registry.enable_provider(name)
            configured_count += 1
        else:
            print(f"✗ {name.capitalize()} NOT configured (missing {env_var})")
            registry.disable_provider(name)

    if configured_count == 0:
        print("\n❌ Error: No providers are configured. Please check your API keys.")
        sys.exit(1)

    # 3. Create Sample Request
    print("\nCreating sample request...")
    request = PromptRequest(
        user_id=1,
        topic="Explain Python decorators",
        objective="Understand Python decorators, inner functions, and wrapper behavior",
        learning_style="step_by_step",
        difficulty="intermediate",
        education_level="college",
        output_length="moderate",
    )
    request.id = 101

    # Initialize Live Council Service
    live_council = LiveCouncil(provider_registry=registry)
    executor = live_council.council_executor

    # 4. Execute Pipeline with Timings
    print("\nExecuting live council workflow...")
    total_start = time.time()

    # Step 1: Provider Execution
    provider_start = time.time()
    try:
        responses = await executor.execute_council(request)
        provider_time = time.time() - provider_start
    except Exception as e:
        print(f"\n❌ Error during provider execution: {e}")
        sys.exit(1)

    # Step 2: Consensus Builder
    consensus_start = time.time()
    try:
        consensus = live_council.consensus_builder.build_consensus(
            responses=responses,
            request_id=request.id
        )
        consensus_time = time.time() - consensus_start
    except Exception as e:
        print(f"\n❌ Error building consensus: {e}")
        sys.exit(1)

    # Step 3: Scorer
    try:
        score = live_council.prompt_scorer.score_prompt(
            consensus_result=consensus,
            learning_style=request.learning_style
        )
    except Exception as e:
        print(f"\n❌ Error scoring prompt: {e}")
        sys.exit(1)

    # Step 4: Explanation Generator
    try:
        explanation = live_council.explanation_generator.generate_full_explanation(
            consensus_result=consensus,
            score=score,
            learning_style=request.learning_style
        )
    except Exception as e:
        print(f"\n❌ Error generating explanation: {e}")
        sys.exit(1)

    total_time = time.time() - total_start

    # 5. Display Warnings for failed providers
    if executor.failed_providers:
        print("\n=================================")
        print("WARNINGS")
        print("=================================")
        for failed in executor.failed_providers:
            print(f"⚠️ Warning: Provider '{failed}' failed to generate a response.")

    # 6. Print Provider Responses
    print("\n=================================")
    print("PROVIDER RESPONSES")
    print("=================================")
    for response in responses:
        print(f"Provider: {response.model}")
        print(f"Response Length: {len(response.prompt)} chars")
        print("-" * 30)

    # 7. Print Consensus Result
    print("\n=================================")
    print("CONSENSUS RESULT")
    print("=================================")
    best_model = consensus.response_metadata.get("best_model", "Unknown")
    print(f"Best Provider: {best_model}")
    print(f"Contributors: {', '.join(consensus.contributors)}")
    print(f"Consensus Score: {consensus.quality_score}")
    print(f"Reasoning: {consensus.consensus_reasoning}")
    print("-" * 30)
    print("Final Prompt Snippet:")
    print(consensus.final_prompt[:300] + "...")

    # 8. Print Scoring Output
    print("\n=================================")
    print("PROMPT SCORE")
    print("=================================")
    print(f"Clarity: {score.clarity}/20")
    print(f"Structure: {score.structure}/20")
    print(f"Personalization: {score.personalization}/20")
    print(f"Educational Effectiveness: {score.educational_effectiveness}/20")
    print(f"Depth: {score.depth}/20")
    print(f"Overall: {score.overall_score}/100")
    print(f"Classification: {score.classification}")

    # 9. Print Explanation Output
    print("\n=================================")
    print("EXPLANATIONS")
    print("=================================")
    print(f"Provider Explanation:\n{explanation['provider_explanation']}")
    print()
    print(f"Consensus Explanation:\n{explanation['consensus_explanation']}")
    print()
    print(f"Learning Style Explanation:\n{explanation['learning_style_explanation']}")
    print()
    print(f"Score Explanation:\n{explanation['score_explanation']}")
    print()
    print(f"Summary:\n{explanation['summary']}")

    # 10. Print Timings
    print("\n=================================")
    print("TIMINGS")
    print("=================================")
    for response in responses:
        rt = response.metadata.response_time if (response.metadata and response.metadata.response_time) else 0.0
        print(f"{response.model:<10}: {rt:.2f} sec")
    print("-" * 30)
    print(f"Provider Execution Time: {provider_time:.2f} seconds")
    print(f"Consensus Build Time: {consensus_time:.4f} seconds")
    print(f"Total Pipeline Time: {total_time:.2f} seconds")
    
    # 11. Print Provider Health
    print("\n=================================")
    print("PROVIDER HEALTH")
    print("=================================")
    stats = live_council.council_executor.health_tracker.get_all_provider_stats()
    for provider, status in stats.items():
        print(f"{provider:<10}: {status}")
    print("=================================")


if __name__ == "__main__":
    asyncio.run(run_e2e())
