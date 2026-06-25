from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

from src.models.council_response import CouncilResponse
from src.models.consensus_result import ConsensusResult


class ConsensusBuilderError(Exception):
    """Exception raised when building consensus fails."""
    pass


class ConsensusBuilder:
    """Consensus Builder for the AI Council.

    Analyzes multiple normalized CouncilResponse objects and generates a
    single high-quality consensus result.
    """

    def build_consensus(
        self, responses: list[CouncilResponse], request_id: int = 0
    ) -> ConsensusResult:
        """Validate, analyze, and build a ConsensusResult from provider responses.

        Args:
            responses: List of normalized CouncilResponse objects.
            request_id: Optional ID of the prompt request.

        Returns:
            ConsensusResult: The generated consensus outcome.

        Raises:
            ConsensusBuilderError: If validation or consensus process fails.
        """
        # 1. Validate responses list
        if responses is None:
            raise ConsensusBuilderError("Responses list cannot be None.")
        if not isinstance(responses, list):
            raise ConsensusBuilderError("Responses must be a list.")
        if len(responses) == 0:
            raise ConsensusBuilderError("Responses list cannot be empty.")

        for idx, r in enumerate(responses):
            if r is None or not isinstance(r, CouncilResponse):
                raise ConsensusBuilderError(
                    f"Invalid response object at index {idx}. All elements must be CouncilResponse instances."
                )

            # Ensure all required properties are present
            if not hasattr(r, "prompt") or r.prompt is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty prompt.")
            if not hasattr(r, "reasoning") or r.reasoning is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty reasoning.")
            if not hasattr(r, "strengths") or r.strengths is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty strengths.")
            if not hasattr(r, "score") or r.score is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty score.")

        # 2. Analyze responses and compute attributes
        best_response = self.select_best_response(responses)
        combined_strengths = self.aggregate_strengths(responses)
        consensus_reasoning = self.generate_consensus_reasoning(
            responses, best_response, combined_strengths
        )
        quality_score = self.calculate_consensus_score(responses)
        contributors = self.extract_contributors(responses)

        logger = logging.getLogger(__name__)
        logger.debug("Provider scores averaged to calculate consensus score: %f", quality_score)
        logger.debug("Selected winner: %s", best_response.model)
        logger.debug("Consensus score value before result creation: %f", quality_score)

        # 3. Return ConsensusResult
        return ConsensusResult(
            request_id=request_id,
            final_prompt=best_response.prompt,
            consensus_reasoning=consensus_reasoning,
            combined_strengths=combined_strengths,
            quality_score=quality_score,
            contributors=contributors,
            response_count=len(responses),
            response_metadata={
                "best_model": best_response.model,
                "best_role": best_response.role,
                "contributors_count": len(contributors),
            }
        )

    def select_best_response(self, responses: list[CouncilResponse]) -> CouncilResponse:
        """Select the best response based on overall score and provider priority tiebreaker.

        Priority order: GPT (highest) > Claude > Gemini > DeepSeek (lowest)
        """
        def get_provider_priority(model_name: str) -> int:
            model_lower = model_name.lower()
            if "gpt" in model_lower:
                return 4
            elif "claude" in model_lower:
                return 3
            elif "gemini" in model_lower:
                return 2
            elif "deepseek" in model_lower:
                return 1
            return 0

        best_response = None
        best_score = -1.0
        best_priority = -1

        for r in responses:
            score = 0.0
            if r.score:
                if r.score.overall_score is not None:
                    score = r.score.overall_score
                else:
                    try:
                        score = r.calculate_overall_score()
                    except Exception:
                        score = 0.0

            priority = get_provider_priority(r.model)

            # High score wins, tie-breaks on provider priority
            if score > best_score:
                best_score = score
                best_priority = priority
                best_response = r
            elif score == best_score:
                if priority > best_priority:
                    best_priority = priority
                    best_response = r
            
            logger = logging.getLogger(__name__)
            logger.debug("Evaluated provider: %s, score: %f", r.model, score)

        if not best_response:
            raise ConsensusBuilderError("Could not determine best response from the list.")
        return best_response

    def aggregate_strengths(self, responses: list[CouncilResponse]) -> list[str]:
        """Collect and deduplicate strengths from all responses while preserving order and ignoring empty values."""
        seen = set()
        combined_strengths = []
        for r in responses:
            for strength in r.strengths:
                if strength and isinstance(strength, str):
                    stripped = strength.strip()
                    if stripped and stripped not in seen:
                        seen.add(stripped)
                        combined_strengths.append(stripped)
        return combined_strengths

    def generate_consensus_reasoning(
        self,
        responses: list[CouncilResponse],
        best_response: CouncilResponse,
        combined_strengths: list[str]
    ) -> str:
        """Generate a text summary explaining consensus contributions, selection, and strengths."""
        has_gpt = False
        has_claude = False
        has_gemini = False
        has_deepseek = False

        for r in responses:
            model_lower = r.model.lower()
            if "gpt" in model_lower or "groq" in model_lower or "llama" in model_lower:
                has_gpt = True
            elif "claude" in model_lower:
                has_claude = True
            elif "gemini" in model_lower:
                has_gemini = True
            elif "deepseek" in model_lower:
                has_deepseek = True

        first_part = ""
        if has_gpt and has_claude:
            first_part = "GPT provided strong educational structure while Claude contributed deeper reasoning"
        elif has_gpt:
            first_part = "GPT provided strong educational structure"
        elif has_claude:
            first_part = "Claude contributed deeper reasoning"

        second_part = ""
        if has_gemini and has_deepseek:
            second_part = "Gemini improved visualization and DeepSeek strengthened logical flow"
        elif has_gemini:
            second_part = "Gemini improved visualization"
        elif has_deepseek:
            second_part = "DeepSeek strengthened logical flow"

        summary_parts = []
        if first_part:
            summary_parts.append(first_part)
        if second_part:
            summary_parts.append(second_part)

        summary = ". ".join(summary_parts)
        if summary:
            summary += "."
        else:
            summary = "Participating council providers contributed to the prompt construction."

        reasoning_end = " The final prompt was selected based on the highest quality score."
        return summary + reasoning_end

    def calculate_consensus_score(self, responses: list[CouncilResponse]) -> float:
        """Average all overall scores and round to 2 decimal places."""
        scores = []
        for r in responses:
            score = 0.0
            if r.score:
                if r.score.overall_score is not None:
                    score = r.score.overall_score
                else:
                    try:
                        score = r.calculate_overall_score()
                    except Exception:
                        score = 0.0
            scores.append(score)

        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def extract_contributors(self, responses: list[CouncilResponse]) -> list[str]:
        """Track unique contributor keys for responses that participated."""
        contributors = []
        for r in responses:
            model_lower = r.model.lower()
            for provider in ["gpt", "claude", "gemini", "deepseek", "groq", "llama"]:
                if provider in model_lower:
                    mapped = provider
                    if provider in ["groq", "llama"]:
                        mapped = "groq"
                    if mapped not in contributors:
                        contributors.append(mapped)
                    break
        return contributors
