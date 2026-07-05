# AI Council Benchmark Report

- **Number of benchmark runs:** 3
- **Average prompt score:** 95.93
- **Average consensus score:** 95.93
- **Average execution time:** 64.72s
- **Fastest provider:** Cerebras
- **Slowest provider:** OpenRouter

## Provider success table
| Provider | Success Rate | Avg Latency (ms) | Wins | Common Error |
|----------|--------------|------------------|------|--------------|
| Groq | 100.0% | 10872.9 | 3 | - |
| OpenRouter | 100.0% | 41783.0 | 0 | - |
| Cerebras | 100.0% | 3363.1 | 0 | - |
| Gemini | 66.7% | 35894.4 | 0 | GeminiTransientError: Gemini transient error: 503 ... |
| Claude | 0.0% | 0.0 | 0 | 400 ClaudeNonTransientError: Claude non-transient ... |
| DeepSeek | 0.0% | 0.0 | 0 | 402 DeepSeekNonTransientError: DeepSeek non-transi... |
| SambaNova | 33.3% | 7143.5 | 0 | 429 SambaNovaRateLimitError: SambaNova rate limit ... |

## Winning provider frequency
- Groq: 3

## Average provider latency
- Groq: 10872.9 ms
- OpenRouter: 41783.0 ms
- Cerebras: 3363.1 ms
- Gemini: 35894.4 ms
- SambaNova: 7143.5 ms

## Example high-quality prompt
- **Topic:** Java
- **Score:** 97.1
- **Winner:** Groq

## Example low-quality prompt
- **Topic:** Python Programming
- **Score:** 93.6
- **Winner:** Groq

## Overall conclusions
The AI Council successfully orchestrates multiple models. The most frequent winner is Groq. Benchmarking complete.
