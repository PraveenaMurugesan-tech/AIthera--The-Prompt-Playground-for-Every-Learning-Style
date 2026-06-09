# AIthera Prompt Library

## Overview

The AIthera Prompt Library contains specialized prompt templates for the Multi-Model AI Council. Each template is designed to leverage the unique strengths of its corresponding AI model to deliver optimized educational content.

## Purpose

AIthera harnesses the collective expertise of four AI models through carefully engineered prompts:

1. **GPT** → Educational Structure Expert
2. **Claude** → Deep Reasoning Expert
3. **Gemini** → Visual Learning Expert
4. **DeepSeek** → Technical Logic Expert

Each prompt template instructs its AI model to generate educational content tailored to a specific pedagogical approach, ensuring learners receive comprehensive, multi-perspective education.

## Template Files

### 1. gpt_teacher.txt
**Model:** GPT-4/GPT-3.5  
**Specialization:** Educational Structure Expert  
**Focus:** Lesson organization, learning progression, clarity, instructional design  
**Output:** Well-structured, progressively scaffolded educational content

### 2. claude_reasoning.txt
**Model:** Claude  
**Specialization:** Deep Reasoning Expert  
**Focus:** Conceptual understanding, critical thinking, reflection, deeper insights  
**Output:** Prompts that develop reasoning skills and conceptual mastery

### 3. gemini_visual.txt
**Model:** Gemini  
**Specialization:** Visual Learning Expert  
**Focus:** Analogies, examples, diagrams, flowcharts, visual explanations  
**Output:** Visually-oriented content optimized for visual learners

### 4. deepseek_logic.txt
**Model:** DeepSeek  
**Specialization:** Technical Logic Expert  
**Focus:** Logical progression, precision, technical accuracy, systematic explanations  
**Output:** Step-by-step logical breakdowns with strong technical precision

## Input Variables (Supported in All Templates)

Each template accepts the following variables:

- **{topic}** - The subject matter or concept to teach
- **{objective}** - The specific learning goal or competency
- **{learning_style}** - Target learning preference (visual, auditory, kinesthetic, reading/writing)
- **{difficulty}** - Content difficulty level (beginner, intermediate, advanced, expert)
- **{education_level}** - Target audience (elementary, middle, high school, undergraduate, graduate, professional)
- **{output_length}** - Desired output length (brief, moderate, comprehensive, detailed)

## How Templates Are Used

### Execution Flow in AI Council

1. **Input Reception**: User submits a learning request with populated input variables
2. **Template Selection**: System selects the appropriate prompt template based on the user's needs
3. **Variable Substitution**: Input variables are substituted into template placeholders
4. **Model Invocation**: The customized prompt is sent to the designated AI model
5. **Response Generation**: The AI model generates specialized educational content
6. **Consensus Processing**: Responses from all four models are processed for consensus scoring
7. **Output Delivery**: Final synthesized response is delivered to the learner

### Example Usage

```
Topic: Photosynthesis
Objective: Understand the light-dependent and light-independent reactions
Learning Style: Visual
Difficulty: Intermediate
Education Level: High School
Output Length: Comprehensive
```

All four templates would receive these values, generating four specialized perspectives on photosynthesis.

## Expected Inputs and Outputs

### Input Format
```
Topic: {topic}
Objective: {objective}
Learning Style: {learning_style}
Difficulty: {difficulty}
Education Level: {education_level}
Output Length: {output_length}
```

### Output Format

Each template generates educational content with:

- **Clear Structure**: Organized sections with logical flow
- **Explanatory Depth**: Appropriate to the difficulty and education level
- **Engagement**: Suited to the target learning style
- **Pedagogical Quality**: Following best practices for the specialized role
- **Actionable Content**: Practical examples, questions, or activities where appropriate

## Template Specifications

### Common Structure (All Templates)

Each template file contains:

1. **Role Definition** - The AI model's specialized role
2. **Context** - Educational framework and objectives
3. **Topic Placeholder** - {topic} insertion point
4. **Objective Placeholder** - {objective} insertion point
5. **Learning Style Consideration** - How to tailor for {learning_style}
6. **Difficulty Adaptation** - Guidance for {difficulty} level
7. **Education Level Adjustment** - Personalization for {education_level}
8. **Output Length Configuration** - Guidelines for {output_length}
9. **Explicit Instructions** - Clear directives for the AI model
10. **Expected Output Format** - Quality criteria and structure

## Production Status

✅ **Production Ready** - All templates are fully functional and ready for integration with the AI Council consensus engine.

## Future Enhancements

- Additional specialized roles (Socratic Method Expert, Storytelling Expert)
- Multi-language template variants
- Domain-specific templates (Math, Sciences, Languages, etc.)
- Integration with adaptive learning algorithms
- Template versioning and performance tracking

---

**Version:** 1.0  
**Last Updated:** 2026-06-09  
**Status:** Production Ready
