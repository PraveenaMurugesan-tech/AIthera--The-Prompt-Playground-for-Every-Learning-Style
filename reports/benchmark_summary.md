# AI Council Benchmark Report

- **Number of benchmark runs:** 3
- **Average prompt score:** 93.37
- **Average consensus score:** 93.37
- **Average confidence score:** 11.06
- **Average agreement score:** 0.14
- **Average diversity score:** 87.51
- **Average coverage score:** 71.43
- **Average completeness score:** 85.71
- **Average learning style score:** 100.00
- **Average learning style accuracy:** 100.00
- **Most common conflict:** None
- **Average successful providers:** 5.00
- **Average execution time:** 61.00s
- **Average validation score:** 90.00
- **Average recommendations:** 0.67
- **Cache hit ratio:** 0.0%
- **Average parallel efficiency:** 93.1%
- **Fastest provider:** Cerebras
- **Slowest provider:** OpenRouter

## Provider success table
| Provider | Success Rate | Avg Latency (ms) | Wins | Common Error |
|----------|--------------|------------------|------|--------------|
| Groq | 100.0% | 8741.0 | 0 | - |
| Gemini | 100.0% | 39192.3 | 0 | - |
| OpenRouter | 100.0% | 56695.2 | 0 | - |
| Cerebras | 100.0% | 3261.5 | 0 | - |
| SambaNova | 100.0% | 7360.4 | 0 | - |
| Claude | 0.0% | 0.0 | 0 | 400 ClaudeNonTransientError: Claude non-transient ... |
| DeepSeek | 0.0% | 0.0 | 0 | 402 DeepSeekNonTransientError: DeepSeek non-transi... |

## Winning provider frequency
- groq: 3

## Average provider latency
- Groq: 8741.0 ms
- Gemini: 39192.3 ms
- OpenRouter: 56695.2 ms
- Cerebras: 3261.5 ms
- SambaNova: 7360.4 ms

## Provider Rankings (Phase 4)
| Rank | Provider | Score | Success Rate | Avg Latency |
|------|----------|-------|--------------|-------------|
| 1 | Cerebras | 99.1 | 100.0% | 3.3s |
| 2 | SambaNova | 96.2 | 100.0% | 7.4s |
| 3 | Groq | 95.2 | 100.0% | 8.7s |
| 4 | Gemini | 80.0 | 100.0% | 39.2s |
| 5 | OpenRouter | 80.0 | 100.0% | 56.7s |
| 6 | Claude | 0.0 | 0.0% | 0.0s |
| 7 | DeepSeek | 0.0 | 0.0% | 0.0s |

## Example high-quality prompt
- **Topic:** Data Structures
- **Score:** 96.6
- **Winner:** groq

## Example low-quality prompt
- **Topic:** Python Programming
- **Score:** 87.0
- **Winner:** groq

## Overall conclusions
The AI Council successfully orchestrates multiple models. The most frequent winner is groq. Benchmarking complete.
