# AIthera Learning Style Rules

This document defines how AIthera adapts educational prompt generation for different learning styles. It is intended as a system design reference for the Learning Style Engine and AI Council adaptation layer.

## Purpose

- Define learner style categories supported by AIthera.
- Describe the information presentation and prompt adaptation rules for each style.
- Provide implementation guidance for the Learning Style Engine.
- Ensure prompt generation aligns with learner preferences, cognitive modes, and assessment goals.

---

## Visual Learner

### Description

Visual learners comprehend information best through imagery, spatial organization, and graphical relationships. They prefer prompts that rely on visual metaphors, diagrams, and structured layouts.

### Learning Characteristics

- Strong preference for images, charts, and diagrams.
- Learns well from spatial organization and visual patterns.
- Retains information when relationships are shown visually.
- Prefers concept mapping and visual summaries.

### Teaching Methods

- Use diagrams, flowcharts, and visual metaphors.
- Break content into visual segments.
- Provide annotated examples and visual comparisons.
- Reinforce concepts with imagery-based analogies.

### Prompt Adaptations

- Instruct AI to include visual descriptors and layout cues.
- Format prompts with headings, bullet lists, and numbered steps.
- Suggest creating concept maps and structured visual breakdowns.
- Prioritize explicit references to diagrams, tables, or graphic organizers.

### Recommended Output Structure

- Clear section headings
- Bulleted or numbered lists
- Visual analogy explanations
- Summary boxes or callouts
- Step bindings with descriptive labels

### Content Emphasis

- Visual relationships between concepts
- Comparative examples and analogies
- Diagram-friendly explanations
- Spatial or hierarchical structures

### Avoid Guidelines

- Avoid dense paragraphs of text.
- Avoid overly abstract or purely verbal explanations.
- Avoid long prose without visual cues.
- Avoid unstructured narrative flow.

### Example Educational Approach

Present the concept using a diagram-like sequence:

- Define the main concept.
- Show key components as labeled sections.
- Compare with a familiar image or metaphor.
- Summarize with a visual-style checklist.

---

## Conversational Learner

### Description

Conversational learners engage through dialogue, narrative, and interactive language. They benefit from prompts that feel like a conversation and encourage reflective thinking.

### Learning Characteristics

- Prefers question-and-answer formats.
- Learns through dialogue and storytelling.
- Retains information when it is presented interactively.
- Responds well to prompts that invite reflection.

### Teaching Methods

- Use conversational tone and guided questions.
- Present content as dialogue or scenario.
- Encourage learner response and reflection.
- Use narrative examples and real-world contexts.

### Prompt Adaptations

- Frame prompts as conversations or mentor guidance.
- Include questions that prompt learner thinking.
- Use natural language and an engaging tone.
- Provide suggestions for follow-up questions.

### Recommended Output Structure

- Conversational openings
- Embedded questions
- Dialogue-style examples
- Reflection prompts and prompts for self-check

### Content Emphasis

- Interactive language and questions
- Storytelling and real-life scenarios
- Learner involvement through prompts
- Explanatory tone with supportive guidance

### Avoid Guidelines

- Avoid formal, academic tone.
- Avoid purely expository or lecture-style content.
- Avoid dense technical descriptions without context.
- Avoid passive statements without learner agency.

### Example Educational Approach

Build the prompt as a guided conversation:

- Introduce the topic as if speaking directly to the learner.
- Ask a question to focus attention.
- Offer a simple explanation and invite reflection.
- Suggest a follow-up task or self-check.

---

## Step-by-Step Learner

### Description

Step-by-step learners prefer sequential guidance and explicit procedural instructions. They thrive when material is broken into ordered actions and clear progressions.

### Learning Characteristics

- Prefers clear, ordered steps.
- Learns best with procedural logic and task breakdown.
- Benefits from milestone-based progress.
- Prefers concrete actions over broad theorizing.

### Teaching Methods

- Use numbered sequences and checklists.
- Break the concept into discrete actions.
- Provide clear transitions between steps.
- Reinforce progress and next actions.

### Prompt Adaptations

- Request explicit step-by-step instructions.
- Emphasize order, milestones, and decision points.
- Use checklists and action-oriented language.
- Provide sequential guidance rather than broad summaries.

### Recommended Output Structure

- Numbered steps or stages
- Progress indicators and checkpoints
- Short task-focused paragraphs
- Clear start/end points for each action

### Content Emphasis

- Procedural clarity
- Task sequencing
- Actionable steps
- Problem-solving order

### Avoid Guidelines

- Avoid open-ended or vague summaries.
- Avoid large conceptual leaps without intermediate steps.
- Avoid overly abstract explanations.
- Avoid unstructured information flow.

### Example Educational Approach

Design prompts as an actionable procedure:

- State the goal.
- List the required steps in order.
- Provide a brief explanation for each step.
- Include a final check or verification step.

---

## Exam-Focused Learner

### Description

Exam-focused learners need concise, high-yield content designed for assessment preparation. They prefer prompts that prioritize recall, structure, and test-like practice.

### Learning Characteristics

- Prefers succinct facts and summaries.
- Learns through practice questions and quick review.
- Values clear definitions and exam-style organization.
- Seeks efficiency and direct relevance.

### Teaching Methods

- Use bullet summaries and key takeaways.
- Present practice questions and quick checks.
- Emphasize definitions and critical concepts.
- Provide structured review prompts.

### Prompt Adaptations

- Format content as review notes and quick-reference prompts.
- Include sample questions and answer checkpoints.
- Emphasize exam terminology and high-yield facts.
- Use direct, concise language.

### Recommended Output Structure

- Key point summaries
- Bullet lists of definitions
- Practice question sections
- Quick review or checklist sections

### Content Emphasis

- High-value concepts
- Definitions and formulas
- Exam-style prompts and recall practice
- Structural clarity and brevity

### Avoid Guidelines

- Avoid lengthy narratives or storytelling.
- Avoid overly exploratory or speculative content.
- Avoid unrelated elaboration and tangential examples.
- Avoid ambiguous explanations without clear takeaways.

### Example Educational Approach

Construct prompts for rapid review:

- Outline the main facts.
- Provide 2-3 practice questions.
- Include concise definitions.
- Offer a checklist of what to remember.

---

## Research-Oriented Learner

### Description

Research-oriented learners seek depth, evidence, and analytical perspective. They respond best to prompts that encourage investigation, comparison, and critical thinking.

### Learning Characteristics

- Prefers deep exploration and justification.
- Learns by comparing ideas and evaluating evidence.
- Values context, nuance, and source-aware reasoning.
- Enjoys open-ended tasks and inquiry-based prompts.

### Teaching Methods

- Use comparative analysis and research prompts.
- Present structured inquiry and synthesis tasks.
- Encourage argumentation and source evaluation.
- Emphasize conceptual connections and context.

### Prompt Adaptations

- Request analytical, research-led prompt output.
- Include prompts for evidence gathering and comparison.
- Use language that supports exploration and depth.
- Suggest follow-up questions and synthesis tasks.

### Recommended Output Structure

- Research questions or themes
- Comparative sections or pros/cons lists
- Evidence-based explanation sections
- Recommendations for further investigation

### Content Emphasis

- Depth and nuance
- Comparative insights
- Evidence and reasoning
- Conceptual integration

### Avoid Guidelines

- Avoid overly simplified or superficial summaries.
- Avoid directive procedural language only.
- Avoid ignoring context or source relevance.
- Avoid one-dimensional or formulaic responses.

### Example Educational Approach

Design prompts as an inquiry task:

- Introduce a research question.
- Provide comparison points and evidence cues.
- Suggest a synthesis or conclusion activity.
- Include recommendations for exploration.

---

## Summary Table

| Learning Style | Teaching Methods | Output Format | Focus |
|---|---|---|---|
| Visual Learner | Diagrams, visual metaphors, structured layouts | Headings, bullet lists, visual analogies | Spatial relationships and imagery |
| Conversational Learner | Dialogue, guided questions, narrative examples | Conversational tone, embedded questions, reflection prompts | Engagement and interactive understanding |
| Step-by-Step Learner | Procedural guidance, checklists, milestones | Numbered steps, progress indicators, action-focused items | Sequence and task clarity |
| Exam-Focused Learner | Review prompts, practice questions, summaries | Bullet summaries, definitions, quick-check sections | Recall, structure, high-yield facts |
| Research-Oriented Learner | Comparative analysis, inquiry prompts, evidence evaluation | Research questions, comparative sections, synthesis cues | Depth, context, critical reasoning |
