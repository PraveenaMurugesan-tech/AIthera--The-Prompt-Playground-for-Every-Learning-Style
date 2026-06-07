# AIthera Input Schema

This document defines the official input contract for AIthera — The Prompt Playground for Every Learning Style. It is the authoritative reference for frontend applications, backend APIs, the AI Council engine, and the Consensus Builder.

The schema establishes a shared contract for request validation, payload normalization, and downstream consumption by AI systems.

---

## 1. Purpose

The input schema provides a stable, machine-readable contract for all components that participate in prompt generation.

It ensures that:

- frontend applications send consistent data,
- backend APIs validate requests correctly,
- the AI Council receives normalized prompt instructions,
- the Consensus Builder uses predictable metadata.

This contract reduces integration errors, improves developer productivity, and supports extensibility without breaking existing clients.

---

## 2. Input Request Structure

The official request payload follows this JSON structure:

```json
{
  "topic": "Photosynthesis",
  "objective": "Understand the complete process",
  "learning_style": "visual",
  "difficulty": "intermediate",
  "education_level": "high_school",
  "output_length": "medium"
}
```

Each field is defined to support clear educational intent, learner preference, and output formatting.

---

## 3. Field Definitions

### topic

- Type: `string`
- Required: `Yes`
- Description: The subject the learner wants to study.
- Validation:
  - Minimum 3 characters
  - Maximum 200 characters
  - Cannot be empty or whitespace only
- Example: `"Photosynthesis"`

---

### objective

- Type: `string`
- Required: `Yes`
- Description: What the learner wants to achieve with the prompt.
- Validation:
  - Minimum 5 characters
  - Maximum 500 characters
  - Cannot be empty or whitespace only
- Example: `"Understand the complete process"`

---

### learning_style

- Type: `enum`
- Required: `Yes`
- Allowed Values:
  - `visual`
  - `conversational`
  - `step_by_step`
  - `exam_focused`
  - `research_oriented`
- Description: Preferred learning method for the generated prompt.
- Validation:
  - Value must match one of the allowed values exactly.
- Example: `"visual"`

---

### difficulty

- Type: `enum`
- Required: `No`
- Allowed Values:
  - `beginner`
  - `intermediate`
  - `advanced`
- Default: `intermediate`
- Description: Desired complexity level for the prompt.
- Validation:
  - If provided, value must match one of the allowed values.
- Example: `"intermediate"`

---

### education_level

- Type: `enum`
- Required: `No`
- Allowed Values:
  - `elementary`
  - `middle_school`
  - `high_school`
  - `undergraduate`
  - `postgraduate`
  - `professional`
- Default: `high_school`
- Description: Educational stage of the learner.
- Validation:
  - If provided, value must match one of the allowed values.
- Example: `"high_school"`

---

### output_length

- Type: `enum`
- Required: `No`
- Allowed Values:
  - `short`
  - `medium`
  - `long`
- Default: `medium`
- Description: Requested length of the generated output.
- Validation:
  - If provided, value must match one of the allowed values.
- Example: `"medium"`

---

## 4. Required Fields

The following fields are required in every valid request:

- `topic`
- `objective`
- `learning_style`

---

## 5. Optional Fields

The following fields are optional but recommended for richer prompt generation:

- `difficulty`
- `education_level`
- `output_length`

---

## 6. Validation Rules

The input contract uses strict validation to ensure safe and predictable processing.

| Rule | Description | Failure Response |
|---|---|---|
| Empty field checks | Required fields cannot be missing, empty, or whitespace only | `{"error": "Missing or empty field", "field": "topic"}` |
| Invalid enum values | Enum fields must match allowed values exactly | `{"error": "Invalid learning_style", "allowed_values": [ ... ]}` |
| String length validation | `topic` and `objective` must meet configured min/max lengths | `{"error": "Invalid objective", "min_length": 5, "max_length": 500}` |
| Input sanitization | Remove dangerous characters and trim whitespace before validation | `{"error": "Unsafe characters detected", "field": "topic"}` |

### Sanitization recommendations

- Trim leading and trailing whitespace
- Normalize unicode characters
- Reject control characters beyond standard text
- Escape or remove script-like content

---

## 7. Example Requests

### Visual learner

```json
{
  "topic": "Photosynthesis",
  "objective": "Understand the complete process of energy conversion in plants",
  "learning_style": "visual",
  "difficulty": "intermediate",
  "education_level": "high_school",
  "output_length": "medium"
}
```

### Exam-focused learner

```json
{
  "topic": "Cell division",
  "objective": "Prepare for a biology exam with key concepts and practice questions",
  "learning_style": "exam_focused",
  "difficulty": "advanced",
  "education_level": "undergraduate",
  "output_length": "short"
}
```

### Research learner

```json
{
  "topic": "Renewable energy policy",
  "objective": "Explore current policy frameworks and compare outcomes across regions",
  "learning_style": "research_oriented",
  "difficulty": "advanced",
  "education_level": "professional",
  "output_length": "long"
}
```

---

## 8. Error Handling

The backend should return structured validation errors that identify the invalid field and provide corrective guidance.

### Sample error responses

#### Invalid enum value

```json
{
  "error": "Invalid learning_style",
  "allowed_values": [
    "visual",
    "conversational",
    "step_by_step",
    "exam_focused",
    "research_oriented"
  ]
}
```

#### Missing required field

```json
{
  "error": "Missing required field",
  "field": "topic"
}
```

#### String length violation

```json
{
  "error": "Invalid objective",
  "field": "objective",
  "min_length": 5,
  "max_length": 500
}
```

#### Input sanitization failure

```json
{
  "error": "Input sanitization failed",
  "field": "topic"
}
```

---

## 9. Future Extensibility

The schema is designed to support backward-compatible extension.

Future fields can be added as optional properties without invalidating existing clients.

### Example future fields

- `preferred_language`
- `accessibility_requirements`
- `subject_category`
- `assessment_type`

### Extension strategy

- Keep new fields optional by default.
- Preserve existing required fields.
- Version the API only when a breaking change is necessary.
- Document additions clearly in the schema reference.

This approach allows the frontend, backend, and AI systems to evolve while maintaining compatibility across existing integrations.
