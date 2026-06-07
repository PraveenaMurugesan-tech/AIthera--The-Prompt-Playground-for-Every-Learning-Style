# AI Response Schema

This document defines the standardized response format used by every AI provider in AIthera's AI Council. The schema supports backend API validation, persistence modeling, and downstream processing for consensus and scoring.

## Purpose

The AI Response Schema establishes a consistent contract for model outputs from GPT, Claude, Gemini, and DeepSeek. It enables:

- standardized parsing across providers,
- reliable scoring and consensus processing,
- error handling for invalid model responses,
- persistence of response metadata and quality signals.

---

## Schema Definition

```json
{
  "provider": "string",
  "response_id": "string",
  "response_text": "string",
  "confidence_score": "number",
  "explanation": "string",
  "learning_style_adjustments": {
    "style": "string",
    "features": ["string"]
  },
  "metadata": {
    "processing_time_ms": "integer",
    "model_version": "string",
    "raw_payload": "object"
  }
}
```

---

## Field Descriptions

### provider

- Type: `string`
- Required: `Yes`
- Description: Identifier for the AI provider that generated this response.
- Example: `"openai_gpt"`

### response_id

- Type: `string`
- Required: `Yes`
- Description: Unique identifier for the response instance.
- Example: `"resp_12345"`

### response_text

- Type: `string`
- Required: `Yes`
- Description: The generated prompt or response content.
- Example: `"Explain photosynthesis in a visual way..."`

### confidence_score

- Type: `number`
- Required: `No`
- Description: Provider confidence or quality estimation normalized to a 0.0–1.0 scale.
- Example: `0.87`

### explanation

- Type: `string`
- Required: `No`
- Description: Optional rationale or reasoning provided by the model.
- Example: `"This prompt emphasizes visual structure to support the learner."`

### learning_style_adjustments

- Type: `object`
- Required: `No`
- Description: Metadata that describes how the output was adapted for the requested learning style.
- Fields:
  - `style`: `string` — learning style identifier
  - `features`: `array[string]` — adaptation features included
- Example:
  ```json
  {
    "style": "visual",
    "features": ["diagram cues", "bullet structure"]
  }
  ```

### metadata

- Type: `object`
- Required: `No`
- Description: Provider-specific and processing metadata for debugging and analytics.
- Fields:
  - `processing_time_ms`: `integer`
  - `model_version`: `string`
  - `raw_payload`: `object`
- Example:
  ```json
  {
    "processing_time_ms": 285,
    "model_version": "gpt-4.1",
    "raw_payload": {}
  }
  ```

---

## Data Types

| Field | Type | Notes |
|---|---|---|
| `provider` | `string` | Required provider identifier |
| `response_id` | `string` | Required unique id |
| `response_text` | `string` | Required generated content |
| `confidence_score` | `number` | Optional normalized score 0.0–1.0 |
| `explanation` | `string` | Optional rationale text |
| `learning_style_adjustments` | `object` | Optional adaptation metadata |
| `metadata` | `object` | Optional provider/process metadata |

---

## Required Fields

- `provider`
- `response_id`
- `response_text`

---

## Optional Fields

- `confidence_score`
- `explanation`
- `learning_style_adjustments`
- `metadata`

---

## Validation Rules

Use the following rules when validating AI provider responses.

| Rule | Description | Example Failure Response |
|---|---|---|
| Required field missing | `provider`, `response_id`, or `response_text` must be present | `{ "error": "Missing required field", "field": "response_text" }` |
| Invalid data type | Field must match defined type | `{ "error": "Invalid field type", "field": "confidence_score", "expected": "number" }` |
| Empty string | Required string fields cannot be empty or whitespace only | `{ "error": "Empty field", "field": "provider" }` |
| Confidence out of range | `confidence_score` must be between 0.0 and 1.0 | `{ "error": "Invalid confidence_score", "min": 0.0, "max": 1.0 }` |
| Invalid enum-like value | `learning_style_adjustments.style` should be a valid style identifier if present | `{ "error": "Invalid learning_style_adjustments.style", "allowed": ["visual", "conversational", "step_by_step", "exam_focused", "research_oriented"] }` |

### Additional validation behaviors

- Trim whitespace from string values before persisting.
- Preserve `metadata.raw_payload` as an opaque object for debugging.
- Reject malformed JSON objects or arrays in structured fields.

---

## Example Responses

### Example 1: GPT response

```json
{
  "provider": "openai_gpt",
  "response_id": "resp_gpt_001",
  "response_text": "Explain photosynthesis with a clear introduction, numbered steps, and a summary.",
  "confidence_score": 0.92,
  "explanation": "This response provides a structured scaffold for the learner.",
  "learning_style_adjustments": {
    "style": "visual",
    "features": ["headings", "bullet lists", "diagram cues"]
  },
  "metadata": {
    "processing_time_ms": 310,
    "model_version": "gpt-4.1",
    "raw_payload": {}
  }
}
```

### Example 2: Claude response

```json
{
  "provider": "anthropic_claude",
  "response_id": "resp_claude_002",
  "response_text": "Describe the principle of energy conversion in plants and the role of chlorophyll.",
  "confidence_score": 0.89,
  "explanation": "Claude emphasizes conceptual depth and the underlying mechanisms.",
  "learning_style_adjustments": {
    "style": "research_oriented",
    "features": ["conceptual framing", "analytic emphasis"]
  },
  "metadata": {
    "processing_time_ms": 365,
    "model_version": "claude-3",
    "raw_payload": {}
  }
}
```

### Example 3: Gemini response

```json
{
  "provider": "google_gemini",
  "response_id": "resp_gemini_003",
  "response_text": "Use the image of a sunlight-powered factory to explain the stages of photosynthesis.",
  "confidence_score": 0.85,
  "explanation": "Gemini provides an illustrative analogy to improve comprehension.",
  "learning_style_adjustments": {
    "style": "visual",
    "features": ["visual metaphor", "example scenario"]
  },
  "metadata": {
    "processing_time_ms": 295,
    "model_version": "gemini-1",
    "raw_payload": {}
  }
}
```

### Example 4: DeepSeek response

```json
{
  "provider": "deepseek",
  "response_id": "resp_deepseek_004",
  "response_text": "List the sequence of chemical reactions and the conditions required for each stage.",
  "confidence_score": 0.91,
  "explanation": "DeepSeek supplies procedural accuracy and technical consistency.",
  "learning_style_adjustments": {
    "style": "step_by_step",
    "features": ["ordered steps", "process logic"]
  },
  "metadata": {
    "processing_time_ms": 340,
    "model_version": "deepseek-v1",
    "raw_payload": {}
  }
}
```

---

## Error Handling

When provider responses fail validation, return structured API errors that identify the failing field and corrective guidance.

### Missing required field

```json
{
  "error": "Missing required field",
  "field": "response_text"
}
```

### Invalid type

```json
{
  "error": "Invalid field type",
  "field": "confidence_score",
  "expected": "number"
}
```

### Out of range value

```json
{
  "error": "Invalid confidence_score",
  "min": 0.0,
  "max": 1.0
}
```

### Invalid nested property

```json
{
  "error": "Invalid learning_style_adjustments.style",
  "allowed_values": [
    "visual",
    "conversational",
    "step_by_step",
    "exam_focused",
    "research_oriented"
  ]
}
```

---

## Backend and Database Implementation Notes

- Store each response as a normalized object with provider metadata.
- Persist `provider`, `response_id`, `response_text`, and `confidence_score` in core response tables.
- Store `learning_style_adjustments` and `metadata` as JSON payloads when using document-capable storage.
- Use the schema for API request validation and backend contract enforcement.
- Keep `raw_payload` for debugging provider-specific output without changing core schema semantics.
