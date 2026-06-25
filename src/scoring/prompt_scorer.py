"""
Prompt Scorer - Phase 17

Evaluates the educational quality of a consensus prompt across five core dimensions:
Clarity, Structure, Personalization, Educational Effectiveness, and Depth.
Categorized scores range from 0 to 20, with the overall score calculated as their sum (0 to 100).
"""

from typing import Any, Optional
import logging
import re
from pydantic import BaseModel, Field

from src.models.consensus_result import ConsensusResult

logger = logging.getLogger(__name__)


class PromptScoringError(Exception):
    """Exception raised when prompt scoring fails due to invalid inputs or processing errors."""
    pass


class ResponseScore(BaseModel):
    """Quality metrics evaluated for a consensus prompt.

    Compatible with serialization. Range for category scores is 0-20.
    Overall score is the sum of category scores (0-100).
    """
    clarity: float = Field(..., description="Clarity and readability score, range 0.0 to 20.0", ge=0.0, le=20.0)
    structure: float = Field(..., description="Structural and formatting quality score, range 0.0 to 20.0", ge=0.0, le=20.0)
    personalization: float = Field(..., description="Personalization alignment score, range 0.0 to 20.0", ge=0.0, le=20.0)
    depth: float = Field(..., description="Conceptual depth and richness score, range 0.0 to 20.0", ge=0.0, le=20.0)
    educational_effectiveness: float = Field(..., description="Pedagogical effectiveness score, range 0.0 to 20.0", ge=0.0, le=20.0)
    overall_score: float = Field(..., description="Overall quality score, range 0.0 to 100.0", ge=0.0, le=100.0)
    classification: Optional[str] = Field(None, description="Quality classification (Excellent, Good, Fair, Poor)")
    notes: Optional[str] = Field(None, description="Detailed evaluation notes")

    def to_dict(self, **kwargs) -> dict[str, Any]:
        """Convert the response score instance to a clean Python dictionary.

        Supports both Pydantic v1 (using `.dict()`) and v2 (using `.model_dump()`).
        """
        if hasattr(self, "model_dump"):
            return self.model_dump(**kwargs)
        return self.dict(**kwargs)


class PromptScorer:
    """Scoring engine that evaluates consensus prompts.

    Derived from docs/SCORING_RULES.md, using a 0-20 range per category
    and a 0-100 range for the overall sum of category scores.
    """

    def __init__(self) -> None:
        """Initialize PromptScorer."""
        pass

    def _validate_prompt(self, prompt: Any) -> None:
        """Helper to validate that a prompt is a non-empty string.

        Raises:
            PromptScoringError: If validation fails.
        """
        if prompt is None:
            raise PromptScoringError("Prompt cannot be None.")
        if not isinstance(prompt, str):
            raise PromptScoringError("Prompt must be a string.")
        if not prompt.strip():
            raise PromptScoringError("Prompt cannot be empty or contain only whitespace.")

    def _calculate_readability(self, prompt: str) -> float:
        """Calculate a readability score for the prompt between 0.0 and 20.0.

        Evaluates average sentence length in words and average word length in characters.
        """
        # Clean and split sentences
        sentences = [s.strip() for s in re.split(r'[.!?\n]', prompt) if s.strip()]
        # Split words
        words = [w.strip() for w in re.split(r'\s+', prompt) if w.strip()]

        if not words:
            return 0.0

        total_sentences = max(len(sentences), 1)
        avg_sentence_len = len(words) / total_sentences

        # Heuristic 1: Sentence length (ideal: 8 to 22 words)
        sentence_score = 0.0
        if 8.0 <= avg_sentence_len <= 22.0:
            sentence_score = 10.0
        elif 22.0 < avg_sentence_len <= 30.0:
            sentence_score = 6.0
        elif avg_sentence_len < 8.0:
            sentence_score = 8.0
        else:
            sentence_score = 3.0

        # Heuristic 2: Word length (characters per word, ideal: 4.0 to 6.5)
        total_chars = sum(len(w) for w in words)
        avg_word_len = total_chars / len(words)

        word_score = 0.0
        if 4.0 <= avg_word_len <= 6.5:
            word_score = 10.0
        else:
            word_score = 5.0

        return sentence_score + word_score

    def _calculate_structure_score(self, prompt: str) -> float:
        """Evaluate the logical arrangement and formatting of the prompt.

        Returns a score between 0.0 and 20.0.
        """
        score = 0.0

        # Heuristic 1: Markdown headers (e.g. #, ##, ###) or bold titles
        if re.search(r'(?m)^#+\s+', prompt) or re.search(r'\*\*.*?\*\*', prompt):
            score += 5.0

        # Heuristic 2: Lists
        has_numbered = bool(re.search(r'(?m)^\d+\.\s+', prompt))
        has_bullet = bool(re.search(r'(?m)^[-\*]\s+', prompt))
        if has_numbered:
            score += 5.0
        elif has_bullet:
            score += 3.0

        # Heuristic 3: Paragraph/section count
        paragraphs = [p for p in prompt.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            score += 5.0
        elif len(paragraphs) == 2:
            score += 3.0
        else:
            score += 1.0

        # Heuristic 4: Logical flow / progression / step keywords
        step_keywords = ["step", "first", "second", "then", "finally", "next", "checkpoint", "sequence", "phase", "milestone"]
        prompt_lower = prompt.lower()
        matched_keywords = sum(1 for kw in step_keywords if kw in prompt_lower)
        score += min(matched_keywords * 1.5, 5.0)

        return min(max(score, 0.0), 20.0)

    def _calculate_personalization_score(self, prompt: str, learning_style: str) -> float:
        """Evaluate how well the prompt is tailored to a specific learning style.

        Returns a score between 0.0 and 20.0.
        """
        if not learning_style:
            return 10.0

        style_normalized = learning_style.lower().strip()
        supported_styles = ["visual", "conversational", "step_by_step", "exam_focused", "research_oriented"]
        if style_normalized not in supported_styles:
            raise PromptScoringError(f"Unsupported learning style: '{learning_style}'.")

        base_score = 8.0
        prompt_lower = prompt.lower()

        # Define keywords for each style
        keywords = {
            "visual": {
                "positive": ["diagram", "flowchart", "map", "visual", "chart", "image", "draw", "graphic", "illustrate", "table", "hierarchy", "structure", "metaphor", "color-coded"],
                "avoid": ["large text blocks", "purely verbal", "dense paragraph", "long prose"]
            },
            "conversational": {
                "positive": ["imagine", "reflect", "think", "you", "feel", "story", "conversation", "dialogue", "ask", "what if", "scenario", "friend", "guided question", "mentor"],
                "avoid": ["formal", "academic", "lecture-style", "theoretical treatment"]
            },
            "step_by_step": {
                "positive": ["step", "sequence", "numbered", "first", "second", "next", "finally", "then", "checkpoint", "procedure", "milestone", "dependency", "algorithm", "pre-requisite"],
                "avoid": ["jumping between", "vague sequencing", "vague step", "conceptual leap"]
            },
            "exam_focused": {
                "positive": ["practice", "quiz", "exam", "test", "question", "recall", "definition", "key concept", "takeaway", "summary", "yield", "assessment", "wrong answer", "mcq", "flashcard"],
                "avoid": ["tangential", "speculative", "unclear assessment", "lecture note"]
            },
            "research_oriented": {
                "positive": ["research", "source", "citation", "evidence", "argument", "theory", "perspective", "analyze", "literature", "reference", "study", "academic", "limitations", "frontiers", "methodology"],
                "avoid": ["unsupported claim", "oversimplification", "purely procedural", "one-dimensional"]
            }
        }

        # Calculate positive keyword matches
        pos_words = keywords[style_normalized]["positive"]
        pos_matches = sum(1 for w in pos_words if w in prompt_lower)
        base_score += min(pos_matches * 1.5, 9.0)

        # Apply negative keyword penalties
        neg_words = keywords[style_normalized]["avoid"]
        neg_matches = sum(1 for w in neg_words if w in prompt_lower)
        base_score -= min(neg_matches * 2.0, 6.0)

        # Apply structural checks
        if style_normalized == "visual" and (re.search(r'(?m)^#+\s+', prompt) or re.search(r'(?m)^[-\*]\s+', prompt)):
            base_score += 3.0
        elif style_normalized == "conversational" and "?" in prompt:
            base_score += 3.0
        elif style_normalized == "step_by_step" and (re.search(r'(?m)^\d+\.\s+', prompt) or re.search(r'(?m)^[-\*]\s+', prompt)):
            base_score += 3.0
        elif style_normalized == "exam_focused" and ("?" in prompt or "practice" in prompt_lower or "quiz" in prompt_lower):
            base_score += 3.0
        elif style_normalized == "research_oriented" and (re.search(r'\[\d+\]', prompt) or re.search(r'\(\w+,\s*\d{4}\)', prompt) or "citation" in prompt_lower):
            base_score += 3.0

        return min(max(base_score, 0.0), 20.0)

    def _calculate_depth_score(self, prompt: str) -> float:
        """Evaluate conceptual depth, detail level, and reasoning of the prompt.

        Returns a score between 0.0 and 20.0.
        """
        score = 0.0
        prompt_len = len(prompt)

        # Heuristic 1: Detail level (length as proxy)
        if prompt_len > 1000:
            score += 8.0
        elif prompt_len > 600:
            score += 6.0
        elif prompt_len > 300:
            score += 4.0
        elif prompt_len > 100:
            score += 2.0

        # Heuristic 2: Reasoning depth keywords
        reasoning_keywords = ["because", "since", "therefore", "why", "how", "reason", "cause", "effect", "mechanism", "process", "underlying", "deep", "explain", "consequence", "influence", "impact"]
        prompt_lower = prompt.lower()
        matched_reasoning = sum(1 for kw in reasoning_keywords if kw in prompt_lower)
        score += min(matched_reasoning * 1.5, 6.0)

        # Heuristic 3: Conceptual richness keywords
        concept_keywords = ["concept", "principle", "theory", "framework", "foundation", "system", "structure", "analysis", "synthesis", "evaluation", "perspective", "hypothesis", "premise"]
        matched_concepts = sum(1 for kw in concept_keywords if kw in prompt_lower)
        score += min(matched_concepts * 1.5, 6.0)

        return min(max(score, 0.0), 20.0)

    def score_clarity(self, prompt: str) -> float:
        """Evaluate clarity and readability.

        Returns:
            float: Score between 0.0 and 20.0.
        """
        self._validate_prompt(prompt)
        readability = self._calculate_readability(prompt)

        # Evaluate action/command verbs
        command_verbs = ["explain", "describe", "define", "compare", "list", "show", "calculate", "write", "analyze", "create", "identify", "solve", "determine", "state"]
        prompt_lower = prompt.lower()
        matched_commands = sum(1 for v in command_verbs if v in prompt_lower)
        verb_score = min(matched_commands * 2.0, 6.0)

        # Evaluate ambiguous phrasing (penalties)
        ambiguous_words = ["maybe", "probably", "stuff", "things", "somehow", "etc", "whatever"]
        matched_ambiguous = sum(1 for w in ambiguous_words if w in prompt_lower)
        penalty = min(matched_ambiguous * 1.5, 4.0)

        # Blend readability, verbs, and ambiguous phrasing
        clarity = (readability * 0.7) + verb_score - penalty
        return round(min(max(clarity, 0.0), 20.0), 2)

    def score_structure(self, prompt: str) -> float:
        """Evaluate formatting and progression structure.

        Returns:
            float: Score between 0.0 and 20.0.
        """
        self._validate_prompt(prompt)
        score = self._calculate_structure_score(prompt)
        return round(score, 2)

    def score_personalization(self, prompt: str, learning_style: str) -> float:
        """Evaluate learning style personalization alignment.

        Returns:
            float: Score between 0.0 and 20.0.
        """
        self._validate_prompt(prompt)
        if learning_style is not None and not isinstance(learning_style, str):
            raise PromptScoringError("Learning style must be a string or None.")
        score = self._calculate_personalization_score(prompt, learning_style)
        return round(score, 2)

    def score_educational_effectiveness(self, prompt: str) -> float:
        """Evaluate examples, learning outcomes, and active engagement guidance.

        Returns:
            float: Score between 0.0 and 20.0.
        """
        self._validate_prompt(prompt)
        score = 0.0
        prompt_lower = prompt.lower()

        # Heuristic 1: Presence of examples
        example_keywords = ["example", "for instance", "e.g.", "such as", "like", "illustration", "case study", "scenario"]
        if any(w in prompt_lower for w in example_keywords):
            score += 5.0

        # Heuristic 2: Pedagogical techniques (active keywords)
        techniques = ["compare", "contrast", "reflect", "practice", "apply", "summarize", "explain", "synthesize", "analyze", "evaluate", "discuss", "solve"]
        matched_tech = sum(1 for t in techniques if t in prompt_lower)
        score += min(matched_tech * 1.0, 5.0)

        # Heuristic 3: Learning outcomes / objectives keywords
        objectives = ["objective", "goal", "will learn", "outcome", "understand", "target", "aim", "purpose"]
        if any(w in prompt_lower for w in objectives):
            score += 5.0

        # Heuristic 4: Active exercises or interactive features
        if "?" in prompt or any(w in prompt_lower for w in ["exercise", "activity", "question", "task", "self-check"]):
            score += 5.0

        return round(min(max(score, 0.0), 20.0), 2)

    def score_depth(self, prompt: str) -> float:
        """Evaluate detail level, reasoning, and conceptual depth.

        Returns:
            float: Score between 0.0 and 20.0.
        """
        self._validate_prompt(prompt)
        score = self._calculate_depth_score(prompt)
        return round(score, 2)

    def score_prompt(
        self,
        consensus_result: ConsensusResult,
        learning_style: str = None
    ) -> ResponseScore:
        """Main entry point to score a consensus result prompt.

        Args:
            consensus_result: The ConsensusResult containing final prompt.
            learning_style: Optional override for style personalization assessment.

        Returns:
            ResponseScore: Reusable Pydantic model populated with evaluation metrics.

        Raises:
            PromptScoringError: On invalid consensus_result or prompt data.
        """
        if consensus_result is None:
            raise PromptScoringError("consensus_result cannot be None.")

        if not isinstance(consensus_result, ConsensusResult):
            raise PromptScoringError("consensus_result must be a ConsensusResult instance.")

        prompt = consensus_result.final_prompt
        self._validate_prompt(prompt)

        # Resolve learning style if not explicitly passed
        if learning_style is None:
            if hasattr(consensus_result, "request") and consensus_result.request is not None:
                learning_style = getattr(consensus_result.request, "learning_style", None)

        if learning_style is not None and not isinstance(learning_style, str):
            raise PromptScoringError("learning_style must be a string or None.")

        clarity = self.score_clarity(prompt)
        structure = self.score_structure(prompt)
        personalization = self.score_personalization(prompt, learning_style)
        educational_effectiveness = self.score_educational_effectiveness(prompt)
        depth = self.score_depth(prompt)

        overall_score = round(clarity + structure + personalization + educational_effectiveness + depth, 2)
        
        # Ensure the consensus_result tracks its own final computed score
        consensus_result.quality_score = overall_score
        logger.debug("Consensus score value returned to the E2E script: %f", overall_score)

        # Quality thresholds (from docs/SCORING_RULES.md, mapped to 0-100 scale)
        if overall_score >= 90.0:
            classification = "Excellent"
        elif overall_score >= 75.0:
            classification = "Good"
        elif overall_score >= 60.0:
            classification = "Fair"
        else:
            classification = "Poor"

        notes = (
            f"Clarity: {clarity}/20, Structure: {structure}/20, Personalization: {personalization}/20, "
            f"Educational Effectiveness: {educational_effectiveness}/20, Depth: {depth}/20. "
            f"Target style: '{learning_style or 'None'}'. Classification: {classification}."
        )

        logger.info("Scored prompt with overall score %f: %s", overall_score, notes)

        return ResponseScore(
            clarity=clarity,
            structure=structure,
            personalization=personalization,
            depth=depth,
            educational_effectiveness=educational_effectiveness,
            overall_score=overall_score,
            classification=classification,
            notes=notes
        )
