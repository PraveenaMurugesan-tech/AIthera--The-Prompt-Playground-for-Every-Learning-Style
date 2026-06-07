# AIthera AI Council Architecture

AIthera is an educational AI platform designed to generate personalized learning prompts through a Multi-Model AI Council. This document describes the full architecture, component responsibilities, consensus workflow, and integration interfaces to guide backend design and implementation.

## 1. Project Vision

### What AIthera Is
AIthera is a prompt intelligence system for education that constructs adaptive prompts instead of fixed answers. It uses multiple AI providers to produce the highest-quality content and tailor it to each learner's preferred style.

### The Problem It Solves
Traditional prompt generation often depends on a single model and yields generic or one-dimensional output. AIthera solves this by combining perspectives from several AI engines, improving relevance, depth, and pedagogical alignment.

### Why Personalized Learning Prompts Matter
Personalized prompts help learners engage with material in a way that matches their cognitive preferences, prior knowledge, and learning goals. They also support retention, motivation, and higher-order thinking by adapting complexity, structure, and examples to the user.

### Why Multiple AI Models Are Used Instead of One
Using multiple models enables a robust ensemble approach where each provider contributes unique strengths. This reduces model-specific bias, increases reliability, and allows the system to produce richer, consensus-driven prompts that are more likely to satisfy diverse educational requirements.

---

## 2. System Objectives

- Personalized learning: adapt prompts to learner preferences and goals.
- Multi-model intelligence: leverage GPT, Claude, Gemini, and DeepSeek together.
- Learning-style adaptation: support visual, conversational, step-by-step, exam-focused, and research-oriented learners.
- Prompt quality optimization: maximize clarity, relevance, structure, and educational effectiveness.
- Explainable AI recommendations: provide rationale for prompt selection and structure.
- Scalable integration: support future AI providers and backend services.

---

## 3. High-Level Architecture

```text
User Request
    ↓
Input Processor
    ↓
Learning Style Engine
    ↓
AI Council
    ├── GPT
    ├── Claude
    ├── Gemini
    └── DeepSeek
    ↓
Response Analyzer
    ↓
Consensus Builder
    ↓
Prompt Scorer
    ↓
Explanation Generator
    ↓
Final Output
```

### Stage Descriptions

- User Request:
  - Learner submits a prompt goal, context, and optional learning preferences.
  - The request contains metadata such as learning style, subject, and assessment objective.

- Input Processor:
  - Normalizes and validates request data.
  - Maps user intention into a standardized input schema.
  - Enriches the request with metadata required by downstream modules.

- Learning Style Engine:
  - Translates learner preferences into prompt adaptation rules.
  - Selects the appropriate style profile and weightings for the AI Council.
  - Ensures output is aligned with visual, conversational, or analytic learning modes.

- AI Council:
  - Simultaneously queries multiple model providers.
  - Collects structured candidate responses from GPT, Claude, Gemini, and DeepSeek.
  - Applies prompt-engineering templates tailored to each provider.

- Response Analyzer:
  - Parses candidate outputs.
  - Extracts semantic structure, examples, tone, and pedagogical value.
  - Flags and normalizes inconsistencies across candidate responses.

- Consensus Builder:
  - Compares and merges candidate recommendations.
  - Identifies the strongest concepts and resolves contradictions.
  - Produces a unified prompt draft.

- Prompt Scorer:
  - Evaluates the draft against scoring criteria.
  - Assigns ratings for clarity, structure, personalization, effectiveness, and depth.
  - Selects the best assembled prompt or triggers a refinement pass.

- Explanation Generator:
  - Produces a rationale document explaining the final prompt.
  - Includes why model recommendations were selected and how learning style shaped the prompt.
  - Supports transparency and future auditing.

- Final Output:
  - Returns the assembled prompt and explanation.
  - Includes metadata, score breakdown, and adaptation notes.

---

## 4. Core Components

### Input Processor

- Purpose:
  - Validate, normalize, and prepare incoming requests for the AI Council.
- Inputs:
  - Raw user request: prompt goal, subject, context, learner profile.
- Outputs:
  - Standardized input payload conforming to `input_schema.json`.
- Responsibilities:
  - Schema validation.
  - Intent extraction.
  - Metadata mapping.
  - Parameter sanitization.

### Learning Style Engine

- Purpose:
  - Generate rules that adapt output to the learner's preferred style.
- Inputs:
  - Learner profile, learning style tags, difficulty settings.
- Outputs:
  - Style adjustment payload with presentation and structure preferences.
- Responsibilities:
  - Classify learning styles.
  - Apply style weights to prompt generation.
  - Transform raw preferences into provider-specific instructions.

### AI Council

- Purpose:
  - Aggregate and coordinate output from multiple AI providers.
- Inputs:
  - Standardized prompt request and learning style payload.
- Outputs:
  - Candidate responses from each model provider.
- Responsibilities:
  - Call GPT, Claude, Gemini, DeepSeek adapters.
  - Apply model-specific prompt templates.
  - Collect structured AI responses.

### Response Analyzer

- Purpose:
  - Analyze and normalize candidate outputs.
- Inputs:
  - Raw responses from each AI model.
- Outputs:
  - Parsed response artifacts and quality signals.
- Responsibilities:
  - Extract structure, examples, and rationale.
  - Detect inconsistencies or missing elements.
  - Annotate each candidate with evaluation metadata.

### Consensus Builder

- Purpose:
  - Merge candidate outputs into a single agreed prompt.
- Inputs:
  - Annotated candidate response artifacts.
- Outputs:
  - Unified prompt draft and consensus metadata.
- Responsibilities:
  - Select best ideas from each model.
  - Resolve conflicts using scoring heuristics.
  - Preserve strengths from the ensemble.

### Prompt Scorer

- Purpose:
  - Score the assembled prompt against evaluation criteria.
- Inputs:
  - Consensus prompt draft and learning-style context.
- Outputs:
  - Prompt scorecard and final prompt recommendation.
- Responsibilities:
  - Compute scores for clarity, structure, personalization, effectiveness, and depth.
  - Compare multiple candidate drafts if needed.
  - Choose final output or request refinement.

### Explanation Generator

- Purpose:
  - Create a transparent rationale for how the final prompt was created.
- Inputs:
  - Consensus metadata, model strengths, and style adaptation details.
- Outputs:
  - Explanation text and justification notes.
- Responsibilities:
  - Document selection logic.
  - Correlate learning-style adaptations with the chosen prompt.
  - Provide traceability for future review.

---

## 5. AI Council Design

The AI Council is an ensemble of four specialized models.

### GPT

- Structure:
  - Generates a strong narrative and content layout.
  - Organizes the prompt into clear educational sections.
- Prompt engineering:
  - Uses scaffolding templates, learning objectives, and step-by-step guidance.
- Educational organization:
  - Delivers coherent learning paths, definitions, and progression.

### Claude

- Deep reasoning:
  - Provides conceptual depth and nuanced explanations.
- Conceptual understanding:
  - Focuses on high-level relationships, reasoning chains, and underlying principles.

### Gemini

- Visual explanations:
  - Produces imagery-based descriptions and analogies.
- Examples:
  - Supplies contextual examples, comparisons, and metaphor-driven content.
- Analogies:
  - Builds accessible mental models for learners.

### DeepSeek

- Logical progression:
  - Creates technically precise, logically ordered prompt content.
- Technical precision:
  - Ensures accuracy and practical detail in instructions.

### Why These Strengths Matter
Each model contributes a distinct educational dimension:
- GPT for structure and accessibility.
- Claude for reasoning and depth.
- Gemini for examples and visual guidance.
- DeepSeek for accuracy and logical flow.
This combination improves prompt quality, reduces blind spots, and supports both conceptual and applied learning.

---

## 6. Learning Style Integration

The Learning Style Engine ensures the final prompt matches the learner's preferred mode.

### Visual learners
- More diagrams, imagery, analogies, and structured visual descriptions.
- Prompts emphasize comparisons, labeled steps, and concept maps.

### Conversational learners
- Use dialogue-style interaction, questions, and relatable tone.
- Prompts include prompts for self-reflection and guided conversation.

### Step-by-step learners
- Present tasks as sequential steps with explicit transitions.
- Prompts break complex ideas into ordered actions.

### Exam-focused learners
- Highlight key facts, test-style questions, and concise summaries.
- Prompts include exam-style prompts, review checklists, and success criteria.

### Research-oriented learners
- Promote exploration, evidence gathering, and discussion prompts.
- Prompts encourage investigation, source comparison, and deeper inquiry.

### How Learning Styles Influence Prompt Generation
Learning style weights modify:
- prompt tone and structure,
- example selection,
- output complexity,
- guidance format,
- the recommended sequence of learning activities.

---

## 7. Consensus Generation Strategy

### How responses are collected
- Each provider receives a model-specific prompt and style payload.
- The AI Council gathers structured outputs from GPT, Claude, Gemini, and DeepSeek.

### How strengths are extracted
- Response Analyzer parses each candidate for key contributions.
- The system tags elements such as clarity, reasoning, example quality, and precision.

### How the best ideas are selected
- Consensus Builder ranks elements by strength and relevance.
- It chooses the strongest explanatory paragraphs, example sets, and step structure.

### How conflicting recommendations are resolved
- The system compares competing claims against scoring heuristics.
- It favors consistency with learning objectives and factual alignment.
- If necessary, it preserves multiple perspectives or merges them into a hybrid prompt.

### How the final prompt is assembled
- The builder combines the strongest sections from each model.
- It maintains a coherent narrative, clear transitions, and learner-specific formatting.
- It generates a final prompt draft that is both pedagogically rich and easy to follow.

### Example consensus workflow
1. Input Processor validates the request and passes it to Learning Style Engine.
2. AI Council queries GPT, Claude, Gemini, DeepSeek.
3. Response Analyzer extracts structure, examples, reasoning, and precision flags.
4. Consensus Builder selects GPT's structure, Claude's reasoning, Gemini's examples, and DeepSeek's accuracy.
5. Prompt Scorer evaluates the assembled draft.
6. Explanation Generator documents the selected path and learning-style influence.

---

## 8. Prompt Evaluation Framework

Prompts are scored across these categories:

- Clarity:
  - Is the prompt easy to understand?
  - Are instructions and expectations explicit?

- Structure:
  - Does the prompt have a logical flow?
  - Are sections organized for learning progression?

- Personalization:
  - Does it reflect the learner's style and preferences?
  - Is it tailored to the requested difficulty and context?

- Educational Effectiveness:
  - Will it guide learning toward the objective?
  - Does it support concept mastery and skills development?

- Depth:
  - Does it provide sufficient substance?
  - Are examples, reasoning, and context included?

### How prompts are scored
- Each category returns a numeric score and rationale.
- Scores may be combined into a composite quality rating.
- Lower-scoring drafts can be refined or reassembled until they meet threshold criteria.

---

## 9. Explainability Layer

AIthera provides an explanation for every final prompt.

### What it explains
- Why certain AI recommendations were selected:
  - It shows which provider contributed structure, reasoning, or examples.
- Why the final prompt is structured a certain way:
  - It justifies the sequence, headings, and emphasis.
- How learning styles influenced the result:
  - It maps style rules to prompt elements.

### Why this matters
- Supports developer trust.
- Enables auditing and improvement.
- Helps educators understand prompt rationale.

---

## 10. Future Scalability

Additional models can be added by extending the AI Council and provider adapter layer.

### Future models
- Mistral
- Grok
- Llama
- Specialized educational or domain-specific models

### How the system supports growth
- Provider adapter interfaces allow new models to plug into the AI Council.
- Consensus Builder can accept additional candidate responses.
- Scoring and explanation logic remain model-agnostic.
- New style or domain engines can be added without changing core orchestration.

---

## 11. Responsibilities of Person 1

Person 1 should own:

- Learning Style Engine:
  - design learner profiles, style rules, and adaptation logic.
- AI Council:
  - orchestrate multi-model queries and provider coordination.
- Model Integrations:
  - implement GPT, Claude, Gemini, DeepSeek adapters.
- Consensus Builder:
  - define merging heuristics and conflict resolution strategies.
- Prompt Scoring System:
  - codify evaluation criteria and score aggregation.
- Explanation Generator:
  - build the explainability layer and rationale output.

---

## 12. Interfaces Required By Person 2

Person 2 should implement the following contracts:

- Input Schema:
  - Defines request fields, learner metadata, and prompt context.
  - Enables validation and predictable backend ingestion.
- AI Response Schema:
  - Defines the structure of model responses.
  - Ensures consistent parsing and evaluation.
- Consensus Schema:
  - Defines the merged prompt payload, selected elements, and metadata.
  - Supports traceability and debugging.
- Explanation Schema:
  - Defines rationale output, model contributions, and style influence.
  - Enables transparent reporting.
- Scoring Rules:
  - Defines score categories, thresholds, and interpretation.
  - Supports prompt quality assessment and decision-making.

### Why these interfaces are important
- They separate frontend/back-end concerns.
- They make each module independently testable.
- They reduce integration risk when adding new models.
- They provide a stable contract for API and database design.

---

## Appendix: Key Schema Files

- `schemas/input_schema.json`
- `schemas/ai_response_schema.json`
- `schemas/consensus_schema.json`
- `schemas/explanation_schema.json`

These schema files define the exact payloads used by the Input Processor, AI Council, Consensus Builder, and Explanation Generator.
