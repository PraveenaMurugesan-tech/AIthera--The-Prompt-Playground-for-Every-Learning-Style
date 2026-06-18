# AIthera Live Council - Production Readiness

This document outlines the production readiness of the AIthera Multi-Provider Live Council, covering its architecture, strategies for resilience, and operational guidelines.

## Supported Providers
The AI Council orchestrates prompt generation across the following AI models:
- **Groq** (`llama-3.3-70b-versatile`) - Role: Creator
- **Claude** (`claude-3-5-sonnet`) - Role: Validator
- **Gemini** (`gemini-2.5-flash`) - Role: Refiner
- **DeepSeek** (`deepseek-chat`) - Role: Critic

## Environment Variables
The system requires the following API keys in the `.env` file for proper execution:
- `GROQ_API_KEY`
- `CLAUDE_API_KEY`
- `GEMINI_API_KEY`
- `DEEPSEEK_API_KEY`

Optional environment variables:
- `[PROVIDER]_MODEL`: Override the default model (e.g., `GEMINI_MODEL=gemini-1.5-pro`)
- `[PROVIDER]_TIMEOUT`: Override the default API timeout in seconds.

## Timeout Strategy
To ensure the pipeline is performant and no single provider delays the consensus:
- **Default Timeout:** 20 to 30 seconds per API request.
- Configured at the client level using `asyncio.wait_for` and provider-specific timeout fields.

## Retry Strategy
Transient errors (e.g., rate limits, server overloads, network timeouts) are handled via Tenacity:
- **Max Retries:** 2-3 attempts (depending on the provider).
- **Backoff:** Exponential backoff, starting at 1 second and capped at 5 seconds.
- Non-transient errors (e.g., Invalid API Keys, Bad Requests) fail fast without retrying.

## Failover Behavior
The Live Council is designed to be highly resilient:
- **Partial Failure:** If one or more providers fail, the system suppresses the error, logs a warning, updates health metrics, and continues execution with the successful providers.
- **Total Failure:** If *all* active providers fail, the `LiveCouncil` raises a `CouncilExecutionError`, halting the execution.

## Health Monitoring
The `ProviderHealthTracker` monitors the availability and performance of each AI provider:
- **Metrics Tracked:** Total requests, successful/failed requests, average response time, and success rate percentage.
- **Reporting:** Call `health_tracker.get_all_provider_stats()` to get human-readable status reports like "Healthy (95%)" or "Failing (30%)".

## Execution Architecture
- The `CouncilExecutor` launches all providers concurrently using `asyncio.gather(*tasks, return_exceptions=True)`.
- Provider responses are standardized via the `ResponseNormalizer`.
- Valid responses are sent to the `ConsensusBuilder` to extract strengths and select the highest quality output.
- The `PromptScorer` and `ExplanationGenerator` evaluate the final prompt.
