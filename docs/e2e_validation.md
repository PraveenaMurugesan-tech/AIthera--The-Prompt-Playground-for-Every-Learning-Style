# E2E Live Council Validation Documentation

This document describes how to execute the End-to-End Live Council validation script, which verifies the integration of the multi-provider execution pipeline, consensus engine, evaluation scoring system, and explanation model.

## Prerequisites & Required API Keys

You must configure the API keys for the providers you wish to test in a `.env` file at the root of the project.

At least one valid API key must be present for the pipeline to execute. If a key is missing, the corresponding provider is skipped gracefully, and a warning is printed.

Configure the following variables:

```env
# Provider API Keys
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSy...
CLAUDE_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...

# Optional configurations
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.5-flash
```

## Running the E2E Integration Script

Run the validation script using Python:

```bash
python scripts/test_live_council_e2e.py
```

## Expected Output

When run, the script outputs the configured providers, executes the pipeline using the configured active providers, and prints the result schema, scores, timing metrics, and explanations.

Here is an example structure of the output:

```text
=================================
AI COUNCIL END-TO-END VALIDATION
=================================
✓ Loaded environment from .env
✓ Groq configured
✓ Gemini configured
✗ Claude NOT configured (missing CLAUDE_API_KEY)
✗ Deepseek NOT configured (missing DEEPSEEK_API_KEY)

Creating sample request...

Executing live council workflow...

=================================
PROVIDER RESPONSES
=================================
Provider: llama-3.3-70b-versatile
Response Length: 1250 chars
------------------------------
Provider: gemini-2.5-flash
Response Length: 1100 chars
------------------------------

=================================
CONSENSUS RESULT
=================================
Best Provider: llama-3.3-70b-versatile
Contributors: groq, gemini
Consensus Score: 0.88
Reasoning: GPT provided strong educational structure. Gemini improved visualization. The final prompt was selected based on the highest quality score.
------------------------------
Final Prompt Snippet:
[Leaf structure decorator explanation...]

=================================
PROMPT SCORE
=================================
Clarity: 16.5/20
Structure: 18.0/20
Personalization: 17.5/20
Educational Effectiveness: 16.0/20
Depth: 15.0/20
Overall: 83.0/100
Classification: Good

=================================
EXPLANATIONS
=================================
Provider Explanation:
Groq contributed educational structure while Gemini provided visual learning support.

Consensus Explanation:
The winning response was selected from a pool of 2 candidate responses with a quality score of 0.88. The selection was driven by strength aggregation across contributors, specifically incorporating: Clear structure, visual diagrams. Groq contributed educational structure while Gemini provided visual learning support. Consensus decision: GPT provided strong educational structure. Gemini improved visualization. The final prompt was selected based on the highest quality score.

Learning Style Explanation:
The final prompt breaks learning into clear sequential actions.

Score Explanation:
The prompt achieved a Good rating due to strong structure, personalization, and clarity.

Summary:
Consensus prompt with Good quality, customized for step_by_step learners using contributions from groq, gemini.

=================================
TIMINGS
=================================
Provider Execution Time: 2.15 seconds
Consensus Build Time: 0.0025 seconds
Total Pipeline Time: 2.18 seconds
=================================
```
