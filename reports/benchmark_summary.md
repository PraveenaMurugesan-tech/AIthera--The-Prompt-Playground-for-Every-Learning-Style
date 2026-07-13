# AI Council Benchmark Report

- **Number of benchmark runs:** 3
- **Average prompt score:** 94.40
- **Average consensus score:** 94.40
- **Average confidence score:** 11.16
- **Average agreement score:** 0.16
- **Average diversity score:** 87.18
- **Average coverage score:** 71.43
- **Average completeness score:** 85.71
- **Average learning style score:** 100.00
- **Average learning style accuracy:** 100.00
- **Most common conflict:** None
- **Average successful providers:** 5.00
- **Average execution time:** 54.12s
- **Average validation score:** 92.67
- **Average recommendations:** 1.00
- **Cache hit ratio:** 0.0%
- **Average parallel efficiency:** 88.6%
- **Fastest provider:** Cerebras
- **Slowest provider:** OpenRouter

## Provider success table
| Provider | Success Rate | Avg Latency (ms) | Wins | Common Error |
|----------|--------------|------------------|------|--------------|
| Groq | 100.0% | 12364.9 | 0 | - |
| Gemini | 100.0% | 45803.1 | 0 | - |
| OpenRouter | 100.0% | 46322.3 | 0 | - |
| Cerebras | 100.0% | 3770.9 | 0 | - |
| SambaNova | 100.0% | 7257.1 | 0 | - |
| Claude | 0.0% | 0.0 | 0 | 400 ClaudeNonTransientError: Claude non-transient ... |
| DeepSeek | 0.0% | 0.0 | 0 | 402 DeepSeekNonTransientError: DeepSeek non-transi... |

## Winning provider frequency
- groq: 3

## Average provider latency
- Groq: 12364.9 ms
- Gemini: 45803.1 ms
- OpenRouter: 46322.3 ms
- Cerebras: 3770.9 ms
- SambaNova: 7257.1 ms

## Provider Rankings (Phase 4)
| Rank | Provider | Score | Success Rate | Avg Latency |
|------|----------|-------|--------------|-------------|
| 1 | Cerebras | 98.7 | 100.0% | 3.8s |
| 2 | SambaNova | 96.2 | 100.0% | 7.3s |
| 3 | Groq | 92.6 | 100.0% | 12.4s |
| 4 | Gemini | 80.0 | 100.0% | 45.8s |
| 5 | OpenRouter | 80.0 | 100.0% | 46.3s |
| 6 | Claude | 0.0 | 0.0% | 0.0s |
| 7 | DeepSeek | 0.0 | 0.0% | 0.0s |

## Example high-quality prompt
- **Topic:** Java
- **Score:** 97.6
- **Winner:** groq

## Example low-quality prompt
- **Topic:** Python Programming
- **Score:** 89.5
- **Winner:** groq

## Overall conclusions
The AI Council successfully orchestrates multiple models. The most frequent winner is groq. Benchmarking complete.
