"""Explanation Generator - Phase 18

Generates detailed, human-readable explanations of provider contributions,
consensus outcomes, learning style alignment, and response quality scoring.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from src.models.consensus_result import ConsensusResult
from src.scoring.prompt_scorer import ResponseScore

logger = logging.getLogger(__name__)


class ExplanationGenerationError(Exception):
    """Exception raised when explanation generation fails due to invalid inputs or processing errors."""
    pass


# Mapping of providers to their specific capabilities/aspects and phrasing verbs.
PROVIDER_ASPECTS = {
    "gpt": {
        "name": "GPT",
        "aspects": ["educational structure", "prompt organization"],
        "verb": "contributed"
    },
    "claude": {
        "name": "Claude",
        "aspects": ["reasoning depth", "analytical thinking"],
        "verb": "enhanced"
    },
    "gemini": {
        "name": "Gemini",
        "aspects": ["visual learning support", "concept visualization"],
        "verb": "provided"
    },
    "deepseek": {
        "name": "DeepSeek",
        "aspects": ["technical precision", "logical accuracy"],
        "verb": "added"
    }
}


class ExplanationGenerator:
    """Generates user-friendly explanations summarizing AI council executions."""

    def __init__(self) -> None:
        """Initialize ExplanationGenerator."""
        pass

    def generate_provider_explanation(self, contributors: list[str]) -> str:
        """Explain how each provider contributed to the final result.

        Args:
            contributors: List of provider names (e.g. ['gpt', 'claude']).

        Returns:
            str: Human-readable sentence explaining the contributions.

        Raises:
            ExplanationGenerationError: If input is invalid or contributors are unknown.
        """
        if contributors is None:
            raise ExplanationGenerationError("Contributors list cannot be None.")
        if not isinstance(contributors, list):
            raise ExplanationGenerationError("Contributors must be a list of strings.")
        if not contributors:
            raise ExplanationGenerationError("Contributors list cannot be empty.")

        normalized_keys = []
        for c in contributors:
            if not isinstance(c, str):
                raise ExplanationGenerationError("Contributor names must be strings.")
            c_norm = c.lower().strip()
            matched_key = None
            for key in PROVIDER_ASPECTS:
                if key in c_norm:
                    matched_key = key
                    break
            if not matched_key:
                raise ExplanationGenerationError(f"Unknown contributor: '{c}'")
            if matched_key not in normalized_keys:
                normalized_keys.append(matched_key)

        clauses = []
        for key in normalized_keys:
            info = PROVIDER_ASPECTS[key]
            clauses.append(f"{info['name']} {info['verb']} {info['aspects'][0]}")

        if len(normalized_keys) == 1:
            info = PROVIDER_ASPECTS[normalized_keys[0]]
            return f"{info['name']} {info['verb']} {info['aspects'][0]} and {info['aspects'][1]}."
        elif len(normalized_keys) == 2:
            return f"{clauses[0]} while {clauses[1]}."
        else:
            part1 = ", ".join(clauses[:-1])
            return f"{part1}, while {clauses[-1]}."

    def generate_consensus_explanation(self, consensus_result: ConsensusResult) -> str:
        """Generate explanation describing why the winning response was selected.

        Args:
            consensus_result: The ConsensusResult database/model object.

        Returns:
            str: Description of consensus reason, strengths, contributors, and count.

        Raises:
            ExplanationGenerationError: If consensus_result is invalid or malformed.
        """
        if consensus_result is None:
            raise ExplanationGenerationError("ConsensusResult cannot be None.")

        # Support both SQLAlchemy model, mock objects, and dictionary inputs
        if isinstance(consensus_result, dict):
            contributors = consensus_result.get("contributors")
            combined_strengths = consensus_result.get("combined_strengths")
            response_count = consensus_result.get("response_count")
            consensus_reasoning = consensus_result.get("consensus_reasoning")
            quality_score = consensus_result.get("quality_score")
        else:
            # Verify presence of expected attributes
            required_attrs = ["contributors", "combined_strengths", "response_count", "consensus_reasoning"]
            for attr in required_attrs:
                if not hasattr(consensus_result, attr):
                    raise ExplanationGenerationError(f"ConsensusResult is missing required attribute: '{attr}'")
            contributors = consensus_result.contributors
            combined_strengths = consensus_result.combined_strengths
            response_count = consensus_result.response_count
            consensus_reasoning = consensus_result.consensus_reasoning
            quality_score = getattr(consensus_result, "quality_score", None)

        if contributors is None:
            raise ExplanationGenerationError("ConsensusResult is missing contributors.")
        if combined_strengths is None:
            raise ExplanationGenerationError("ConsensusResult is missing combined_strengths.")
        if response_count is None:
            raise ExplanationGenerationError("ConsensusResult is missing response_count.")
        if not consensus_reasoning:
            raise ExplanationGenerationError("ConsensusResult is missing consensus_reasoning.")

        if not isinstance(contributors, list):
            raise ExplanationGenerationError("contributors must be a list of strings.")
        if not isinstance(combined_strengths, list):
            raise ExplanationGenerationError("combined_strengths must be a list of strings.")
        if not isinstance(response_count, int):
            raise ExplanationGenerationError("response_count must be an integer.")
        if not isinstance(consensus_reasoning, str):
            raise ExplanationGenerationError("consensus_reasoning must be a string.")

        provider_exp = self.generate_provider_explanation(contributors)
        strengths_str = ", ".join(combined_strengths) if combined_strengths else "general capabilities"
        score_str = f" with a quality score of {quality_score:.2f}" if quality_score is not None else ""

        explanation = (
            f"The winning response was selected from a pool of {response_count} candidate responses{score_str}. "
            f"The selection was driven by strength aggregation across contributors, specifically incorporating: {strengths_str}. "
            f"{provider_exp} Consensus decision: {consensus_reasoning}"
        )
        return explanation

    def generate_learning_style_explanation(self, learning_style: str) -> str:
        """Generate human-readable explanation based on learning style.

        Args:
            learning_style: Target style name.

        Returns:
            str: Explanation of styling emphasis.

        Raises:
            ExplanationGenerationError: If learning style is invalid or unsupported.
        """
        if learning_style is None:
            raise ExplanationGenerationError("Learning style cannot be None.")
        if not isinstance(learning_style, str):
            raise ExplanationGenerationError("Learning style must be a string.")

        style_clean = learning_style.strip().lower().replace("_", "-")

        style_map = {
            "visual": "The final prompt emphasizes diagrams, structured layouts, and visual understanding.",
            "conversational": "The final prompt emphasizes discussion, dialogue, and natural explanations.",
            "step-by-step": "The final prompt breaks learning into clear sequential actions.",
            "exam-focused": "The final prompt prioritizes high-yield concepts and exam preparation.",
            "research-oriented": "The final prompt encourages evidence-based exploration and deeper investigation."
        }

        if style_clean not in style_map:
            raise ExplanationGenerationError(f"Unsupported learning style: '{learning_style}'.")

        return style_map[style_clean]

    def _get_score_val(self, score: Any, key: str) -> Optional[float]:
        """Helper to extract a score value from Pydantic, SQLAlchemy model, or dict."""
        for attr in [f"{key}_score", key]:
            val = getattr(score, attr, None)
            if val is not None:
                return float(val)
        if isinstance(score, dict):
            for attr in [f"{key}_score", key]:
                if attr in score:
                    val = score[attr]
                    if val is not None:
                        return float(val)
        return None

    def generate_score_explanation(self, score: ResponseScore) -> str:
        """Generate explanation of ResponseScore classifications and strengths.

        Args:
            score: Quality ResponseScore metrics.

        Returns:
            str: Sentence explaining rating and strengths.

        Raises:
            ExplanationGenerationError: If score is invalid or missing required metrics.
        """
        if score is None:
            raise ExplanationGenerationError("ResponseScore cannot be None.")

        # Extract sub-scores
        clarity = self._get_score_val(score, "clarity")
        structure = self._get_score_val(score, "structure")
        personalization = self._get_score_val(score, "personalization")
        educational_effectiveness = self._get_score_val(score, "educational_effectiveness")
        depth = self._get_score_val(score, "depth")
        overall_score = self._get_score_val(score, "overall_score")

        if (clarity is None and structure is None and personalization is None 
                and educational_effectiveness is None and depth is None and overall_score is None):
            raise ExplanationGenerationError("ResponseScore is missing all rating metrics.")

        classification = getattr(score, "classification", None)
        if isinstance(score, dict):
            classification = score.get("classification")

        # Infer classification if missing
        if not classification:
            if overall_score is not None:
                if overall_score > 1.0:
                    if overall_score >= 90.0:
                        classification = "Excellent"
                    elif overall_score >= 75.0:
                        classification = "Good"
                    elif overall_score >= 60.0:
                        classification = "Average"
                    else:
                        classification = "Poor"
                else:
                    if overall_score >= 0.90:
                        classification = "Excellent"
                    elif overall_score >= 0.75:
                        classification = "Good"
                    elif overall_score >= 0.60:
                        classification = "Average"
                    else:
                        classification = "Poor"
            else:
                classification = "Average"

        if not isinstance(classification, str):
            raise ExplanationGenerationError("Classification must be a string.")

        class_norm = classification.strip().capitalize()
        if class_norm == "Fair":
            class_norm = "Average"

        if class_norm not in ["Excellent", "Good", "Average", "Poor"]:
            raise ExplanationGenerationError(f"Unsupported classification: '{classification}'.")

        # Determine strong areas
        sub_scores = {
            "clarity": clarity,
            "structure": structure,
            "personalization": personalization,
            "educational effectiveness": educational_effectiveness,
            "depth": depth
        }

        valid_subs = {k: v for k, v in sub_scores.items() if v is not None}

        if not valid_subs:
            article = "an" if class_norm in ["Excellent", "Average"] else "a"
            return f"The prompt achieved {article} {class_norm} rating based on the overall evaluation."

        max_val = max(valid_subs.values())
        threshold = 14.0 if max_val > 1.0 else 0.7

        strong_areas = [k for k, v in valid_subs.items() if v >= threshold]

        if not strong_areas:
            sorted_areas = sorted(valid_subs.items(), key=lambda x: x[1], reverse=True)
            strong_areas = [k for k, v in sorted_areas[:2]]

        if len(strong_areas) == 1:
            areas_str = strong_areas[0]
        elif len(strong_areas) == 2:
            areas_str = f"{strong_areas[0]} and {strong_areas[1]}"
        else:
            areas_str = ", ".join(strong_areas[:-1]) + f", and {strong_areas[-1]}"

        article = "an" if class_norm in ["Excellent", "Average"] else "a"

        if class_norm == "Poor":
            return f"The prompt achieved a Poor rating due to weaker performance, but shows some potential in {areas_str}."
        elif class_norm == "Average":
            return f"The prompt achieved an Average rating due to moderate {areas_str}."
        else:
            return f"The prompt achieved {article} {class_norm} rating due to strong {areas_str}."

    def generate_full_explanation(
        self,
        consensus_result: ConsensusResult,
        score: ResponseScore,
        learning_style: str
    ) -> dict:
        """Combine explanations into a full explanation output dictionary.

        Args:
            consensus_result: Selected ConsensusResult.
            score: Evaluated ResponseScore.
            learning_style: target learning style.

        Returns:
            dict: Structured dictionary containing all explanation parts.

        Raises:
            ExplanationGenerationError: If inputs are invalid or malformed.
        """
        if consensus_result is None:
            raise ExplanationGenerationError("ConsensusResult cannot be None.")
        if score is None:
            raise ExplanationGenerationError("ResponseScore cannot be None.")
        if not learning_style:
            raise ExplanationGenerationError("learning_style cannot be None or empty.")

        contributors = getattr(consensus_result, "contributors", None)
        if isinstance(consensus_result, dict):
            contributors = consensus_result.get("contributors")

        if contributors is None:
            contributors = []

        provider_explanation = self.generate_provider_explanation(contributors)
        consensus_explanation = self.generate_consensus_explanation(consensus_result)
        learning_style_explanation = self.generate_learning_style_explanation(learning_style)
        score_explanation = self.generate_score_explanation(score)

        # Build clean summary
        classification = getattr(score, "classification", None)
        if isinstance(score, dict):
            classification = score.get("classification")

        if classification:
            class_str = classification.strip().capitalize()
            if class_str == "Fair":
                class_str = "Average"
        else:
            class_str = "Average"

        contributors_str = ", ".join(contributors) if contributors else "AI Council"
        summary = (
            f"Consensus prompt with {class_str} quality, customized for {learning_style} learners "
            f"using contributions from {contributors_str}."
        )

        return {
            "provider_explanation": provider_explanation,
            "consensus_explanation": consensus_explanation,
            "learning_style_explanation": learning_style_explanation,
            "score_explanation": score_explanation,
            "summary": summary
        }
