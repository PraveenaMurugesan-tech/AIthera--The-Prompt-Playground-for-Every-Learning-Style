# AI Role Definitions

This document defines the responsibilities of each AI model participating in AIthera’s multi-model AI Council. It provides the operational profile for each provider and explains how the models work together to generate consensus-driven educational prompts.

---

## OpenAI GPT

### Primary Role

Prompt architect and structural organizer.

### Mission within the Council

Provide the core prompt framework, narrative organization, and user-facing instructional layout.

### Core Responsibilities

- Generate coherent prompt structures.
- Create clear educational flow.
- Organize content into logical sections.
- Provide accessible explanations and scaffolded guidance.

### Strengths

- Strong natural language fluency.
- Excellent narrative and instructional organization.
- Good at producing readable, learner-friendly text.
- Effective at scaffolding information for broad audiences.

### Weaknesses

- May be less specialized in deep reasoning compared to other models.
- Can produce generic examples if not guided precisely.
- May require support to deepen technical precision.

### Expected Contributions

- Overall prompt structure and sectioning.
- High-level learning objectives and explanation flow.
- Learner-friendly instructions and transitions.

### Prompting Strategy

Use clear guidance, ask for stepwise structure, and emphasize educational organization:

- "Organize this topic into a structured learning prompt..."
- "Provide a clear introduction, steps, and summary..."

### Example Output Characteristics

- Well segmented with headings and bullets.
- Smooth transitions between ideas.
- Balanced tone suitable for learners.
- Clear instructions and supportive language.

### Consensus Contribution

GPT contributes the structural scaffold and narrative backbone. It provides the default format that other model contributions can align with.

---

## Anthropic Claude

### Primary Role

Conceptual deep reasoning and principled explanation.

### Mission within the Council

Provide conceptual clarity, reasoning chains, and high-level insight that deepen the educational prompt.

### Core Responsibilities

- Deliver nuanced conceptual explanations.
- Strengthen reasoning and argument structure.
- Provide principle-based context and interpretation.
- Clarify the underlying logic of the subject matter.

### Strengths

- Deep reasoning and conceptual analysis.
- Good at multi-step logical explanation.
- Strong in high-level conceptual coherence.

### Weaknesses

- May produce more abstract language that requires grounding.
- Can become verbose without structure if not constrained.
- May need help simplifying for certain learner styles.

### Expected Contributions

- Conceptual summaries and reasoning rationale.
- Analytical explanations of why ideas matter.
- High-level framing that supports understanding.

### Prompting Strategy

Ask for explanatory depth and reasoning clarity:

- "Explain the core principles and reasoning behind..."
- "Provide a conceptual breakdown with clear logic..."

### Example Output Characteristics

- Thoughtful analysis and reasoning chains.
- Strong conceptual cohesion.
- Insightful interpretation of core ideas.

### Consensus Contribution

Claude contributes the depth layer, ensuring the final prompt includes strong reasoning and conceptual rigor.

---

## Google Gemini

### Primary Role

Illustrative example generation and visual metaphor support.

### Mission within the Council

Provide engaging examples, analogies, and visual framing to make concepts easier to understand.

### Core Responsibilities

- Generate concrete examples and analogies.
- Support visual and comparative explanations.
- Create imagery-rich descriptions.
- Translate abstract content into accessible forms.

### Strengths

- Strong at visual and analogy-driven explanations.
- Good at example generation.
- Effective at making abstract ideas concrete.

### Weaknesses

- Can over-emphasize metaphor at the expense of precision.
- May require alignment with structural flow.
- May need validation for technical accuracy.

### Expected Contributions

- Visual analogies, examples, and scenario descriptions.
- Comparison-based reasoning.
- Learner-friendly illustrations of key concepts.

### Prompting Strategy

Request examples and visual metaphors explicitly:

- "Provide a visual analogy or illustrative example..."
- "Give a concrete scenario that explains this concept..."

### Example Output Characteristics

- Rich, imagery-based descriptions.
- Strong examples and analogies.
- Comparative language that highlights relationships.

### Consensus Contribution

Gemini contributes the illustrative layer, making the final prompt more vivid and memorable.

---

## DeepSeek

### Primary Role

Technical precision and procedural logic.

### Mission within the Council

Provide accurate, logically ordered content with detail-oriented guidance and procedural clarity.

### Core Responsibilities

- Generate precise, technically sound content.
- Provide stepwise logic and process orientation.
- Reinforce correctness and factual consistency.
- Contribute procedural detail.

### Strengths

- Strong at logical sequencing and technical accuracy.
- Good at detailed procedural instructions.
- Effective at maintaining rigorous content.

### Weaknesses

- Can be less fluid in narrative tone.
- May prioritize precision over readability.
- May need balancing to avoid over-detailing.

### Expected Contributions

- Accurate, stepwise guidance and technical detail.
- Logical flow for problem-solving prompts.
- Factually consistent explanations.

### Prompting Strategy

Ask for detailed sequence and precision:

- "Provide a logically ordered explanation with precise steps..."
- "Ensure the answer is technically accurate and process-oriented..."

### Example Output Characteristics

- Clear procedural sequences.
- Accurate technical detail.
- Logical ordering and verification language.

### Consensus Contribution

DeepSeek contributes the precision and procedural guardrails. It ensures that the final prompt is accurate and logically consistent.

---

## Complementary Model Strategy

These models complement each other rather than compete by contributing different educational dimensions:

- GPT provides broad structure and readability.
- Claude provides depth and concept-oriented reasoning.
- Gemini provides examples, analogies, and visual framing.
- DeepSeek provides precision and procedural clarity.

Together, they produce prompts that are structurally sound, conceptually robust, illustrative, and technically accurate.

---

## Why Multiple AI Models Are Better Than One

A single model often reflects a single perspective. Combining multiple models enables AIthera to leverage complementary strengths and reduce weaknesses.

- Increased reliability: multiple viewpoints reduce single-model bias.
- Better coverage: structure, reasoning, examples, and precision are all represented.
- Higher quality: consensus-driven prompts are more balanced and pedagogically rich.
- Flexible adaptation: different styles can be weighted according to learner needs.

This multi-model strategy produces better educational prompts by ensuring that the final output is not only fluent, but also conceptually deep, memorable, and accurate.

---

## Model Comparison Table

| Model | Role | Strengths | Primary Contribution |
|---|---|---|---|
| OpenAI GPT | Prompt architect and structural organizer | Narrative structure, readability, learner-friendly flow | Prompt framework and user-facing organization |
| Anthropic Claude | Conceptual reasoning specialist | Deep reasoning, conceptual clarity, logical coherence | Conceptual depth and rationale |
| Google Gemini | Illustrative explanation specialist | Visual metaphors, examples, analogies | Example generation and visual framing |
| DeepSeek | Technical precision specialist | Procedural logic, factual accuracy, detail | Precision and stepwise process |

---

## Implementation Guidance for CouncilExecutor and ConsensusBuilder

- CouncilExecutor should invoke all providers in parallel and collect structured responses.
- Each provider response should include metadata identifying its role and contributions.
- ConsensusBuilder should extract the role-specific contributions:
  - GPT for structure and flow.
  - Claude for reasoning and high-level context.
  - Gemini for examples and visual analogies.
  - DeepSeek for precision and procedural order.
- ConsensusBuilder should merge these contributions into a unified prompt while preserving the strongest elements from each model.
- The final consensus prompt should maintain readability, conceptual strength, illustrative clarity, and factual accuracy.
