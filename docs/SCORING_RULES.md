# AIthera Scoring Rules

This document defines the official framework used to evaluate educational prompt quality in AIthera. It guides the PromptScorer service, provides consistent quality thresholds, and supports consensus-based prompt selection.

---

## 1. Purpose

The scoring rules define how final prompts are evaluated across dimensions that matter for educational outcomes. They provide a deterministic contract for the PromptScorer service and help ensure that outputs are both learner-appropriate and pedagogically effective.

---

## 2. Evaluation Philosophy

AIthera evaluates prompts through a balanced, learner-centered lens. The scoring framework prioritizes clarity and structure while ensuring prompts are personalized and educationally meaningful. The goal is to surface the highest-quality prompt candidate from the AI Council and provide transparent quality metrics.

Key principles:

- Use measurable categories with clear definitions.
- Weight categories according to instructional impact.
- Evaluate both content quality and learner alignment.
- Support explainability through explicit criteria.

---

## 3. Scoring Categories

The PromptScorer evaluates final prompts in five categories:

- Clarity
- Structure
- Personalization
- Educational Effectiveness
- Depth

Each category is scored on a normalized scale from 0.0 to 1.0.

---

## 4. Weight Distribution

| Category | Weight | Rationale |
|---|---|---|
| Clarity | 25% | Ensures the prompt is easily understood and actionable |
| Structure | 20% | Ensures logical flow and organization |
| Personalization | 20% | Ensures adaptation to learner style and profile |
| Educational Effectiveness | 25% | Ensures the prompt supports learning outcomes |
| Depth | 10% | Ensures sufficient substance and conceptual richness |

Weights are applied to the normalized category scores to compute the overall score.

---

## 5. Metric Definitions

### Clarity

- Weight: 25%
- Description: Measures how easy the prompt is to understand and follow.
- Evaluation criteria:
  - Uses simple, direct language
  - Has unambiguous instructions
  - Avoids jargon without explanation
  - Includes clear objectives or task statements
- Example indicators:
  - "Explain..." rather than "Discuss..."
  - Single-step instructions that are easy to parse
  - Minimal ambiguous phrasing

### Structure

- Weight: 20%
- Description: Measures the logical arrangement of content and progression.
- Evaluation criteria:
  - Uses headings, sections, or ordered steps when appropriate
  - Maintains coherent flow from introduction to conclusion
  - Groups related elements together
  - Avoids abrupt topic shifts
- Example indicators:
  - Clearly separated introduction, body, and summary
  - Numbered or bulleted steps for procedural prompts
  - Logical sequence of learning activities

### Personalization

- Weight: 20%
- Description: Measures how well the prompt is adapted to the learner’s style and context.
- Evaluation criteria:
  - Reflects the selected learning style
  - Includes relevant examples or tone for the learner
  - Aligns with education level and difficulty
  - Responds to learner-specific goals
- Example indicators:
  - Visual learners receive imagery and structure
  - Conversational learners receive dialogue-style phrasing
  - Exam-focused learners receive review and practice questions

### Educational Effectiveness

- Weight: 25%
- Description: Measures the prompt’s ability to support learning and comprehension.
- Evaluation criteria:
  - Sets a clear learning objective
  - Guides learners toward meaningful understanding
  - Includes pedagogical techniques such as comparison, reflection, or application
  - Avoids prompts that are purely descriptive or irrelevant
- Example indicators:
  - Requests synthesis, explanation, or application
  - Encourages active engagement with the topic
  - Connects the topic to learner goals or assessment needs

### Depth

- Weight: 10%
- Description: Measures whether the prompt offers sufficient conceptual richness.
- Evaluation criteria:
  - Provides more than shallow surface-level instruction
  - Includes meaningful examples or supporting context
  - Supports higher-order thinking when appropriate
  - Avoids overly simplistic phrasing for advanced learners
- Example indicators:
  - Includes explanation of cause/effect or reasoning
  - Provides context or background for the topic
  - Offers concrete examples with educational value

---

## 6. Scoring Methodology

The PromptScorer evaluates each category independently on a score from 0.0 to 1.0. Scores can be derived from:

- rule-based heuristics,
- machine-learned quality models,
- combination of both.

### Evaluation process

1. Parse the final prompt and identify structure, style, and content features.
2. Apply category-specific rules and heuristics.
3. Assign normalized scores for each category.
4. Compute weighted overall score.
5. Generate a score report with category values and notes.

### Example scoring considerations

- Clarity may be reduced for prompts with vague verbs.
- Structure may be penalized for mixed or missing sections.
- Personalization may be reduced if the prompt does not match the selected learning style.
- Educational Effectiveness may be reduced if the prompt lacks a clear learner objective.
- Depth may be reduced if the prompt is merely a definition without supporting explanation.

---

## 7. Overall Score Calculation

The overall score is calculated as a weighted sum of category scores.

```text
overall_score =
  (clarity * 0.25) +
  (structure * 0.20) +
  (personalization * 0.20) +
  (educational_effectiveness * 0.25) +
  (depth * 0.10)
```

The final score should be normalized to the 0.0–1.0 range.

---

## 8. Quality Thresholds

Define thresholds for prompt quality classification.

| Classification | Score Range | Interpretation |
|---|---|---|
| Excellent | 0.90 – 1.00 | High-quality prompt ready for delivery |
| Good | 0.75 – 0.89 | Acceptable prompt with minor improvements |
| Fair | 0.60 – 0.74 | Usable prompt requiring refinement |
| Poor | 0.00 – 0.59 | Prompt needs significant revision |

### Threshold actions

- Excellent: deliver as final output.
- Good: optionally deliver or refine if higher quality is desired.
- Fair: trigger a refinement pass through the AI Council or PromptScorer.
- Poor: reject or request regeneration with stricter guidance.

---

## 9. Consensus Builder Usage

The Consensus Builder uses the score report to:

- compare candidate prompt drafts,
- select the highest-quality assembled prompt,
- identify categories that need refinement,
- enable fallback behavior when no prompt meets quality thresholds.

### Integration rules

- Use the overall score to rank prompt candidates.
- Preserve category-level scores in the consensus output for transparency.
- If multiple candidates have similar overall scores, prefer the one with higher educational effectiveness.
- If scores are below threshold, use the PromptScorer notes to guide regeneration.

---

## 10. Example Score Reports

### Example 1: High-quality prompt

| Category | Score | Notes |
|---|---|---|
| Clarity | 0.95 | Clear instructions and simple wording |
| Structure | 0.90 | Logical layout with numbered steps |
| Personalization | 0.88 | Matches visual learner format |
| Educational Effectiveness | 0.92 | Strong learning objective and engagement |
| Depth | 0.80 | Good supporting context and examples |
| Overall | 0.90 | Excellent prompt ready for delivery |

Calculation:

```text
overall = (0.95*0.25) + (0.90*0.20) + (0.88*0.20) + (0.92*0.25) + (0.80*0.10)
overall = 0.2375 + 0.18 + 0.176 + 0.23 + 0.08 = 0.9035
```

### Example 2: Needs refinement

| Category | Score | Notes |
|---|---|---|
| Clarity | 0.70 | Some ambiguous phrasing |
| Structure | 0.65 | Weak progression between sections |
| Personalization | 0.75 | Learner style reflected, but not strongly |
| Educational Effectiveness | 0.72 | Lacks explicit application guidance |
| Depth | 0.60 | Limited conceptual richness |
| Overall | 0.70 | Fair prompt that requires improvement |

Calculation:

```text
overall = (0.70*0.25) + (0.65*0.20) + (0.75*0.20) + (0.72*0.25) + (0.60*0.10)
overall = 0.175 + 0.13 + 0.15 + 0.18 + 0.06 = 0.695
```

---

## 11. Future Expansion Rules

The scoring framework can be extended while preserving backward compatibility.

### Expansion guidelines

- Add new categories as optional score dimensions, such as `engagement` or `accuracy`.
- Keep existing category definitions stable.
- Introduce new weights via versioned scoring configuration.
- Allow the PromptScorer service to support alternate weighting profiles for different use cases.

### Example future categories

- Engagement
- Accuracy
- Accessibility
- Creativity

---

## 12. Implementation Considerations

### PromptScorer service design

- Accepts a final prompt and metadata from the Consensus Builder.
- Produces category scores, an overall score, threshold classification, and evaluation notes.
- Returns a structured score report.

### Data contract

The score report should include:

- `clarity`
- `structure`
- `personalization`
- `educational_effectiveness`
- `depth`
- `overall_score`
- `classification`
- `notes`

### Performance and reliability

- Scoring should be deterministic for a given prompt.
- Use caching for repeated prompt evaluations when appropriate.
- Log threshold failures and refinement triggers.

### Auditing and traceability

- Persist score reports with final prompt outputs.
- Record the scoring version and weighting configuration.
- Use category-level feedback to drive prompt refinement.

This scoring rules document is designed to support the direct implementation of a PromptScorer service and integration with the Consensus Builder.
