import difflib
import logging
import re
from typing import Any, Dict, List, Optional

from src.models.council_response import CouncilResponse
from src.models.consensus_result import ConsensusResult


class ConsensusBuilderError(Exception):
    """Exception raised when building consensus fails."""
    pass


class ConsensusBuilder:
    """Consensus Builder for the AI Council.

    Analyzes multiple normalized CouncilResponse objects and generates a
    single high-quality consensus result using multi-factor evaluation.
    """

    def build_consensus(
        self, 
        responses: list[CouncilResponse], 
        request_id: int = 0,
        learning_style: str = "visual",
        failed_providers: Optional[list[str]] = None
    ) -> ConsensusResult:
        """Validate, analyze, and build a ConsensusResult from provider responses.

        Args:
            responses: List of normalized CouncilResponse objects.
            request_id: Optional ID of the prompt request.
            learning_style: The target learning style for evaluation.
            failed_providers: List of providers that failed during execution.

        Returns:
            ConsensusResult: The generated consensus outcome.

        Raises:
            ConsensusBuilderError: If validation or consensus process fails.
        """
        if failed_providers is None:
            failed_providers = []
            
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

            if not hasattr(r, "prompt") or r.prompt is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty prompt.")
            if not hasattr(r, "reasoning") or r.reasoning is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty reasoning.")
            if not hasattr(r, "strengths") or r.strengths is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty strengths.")
            if not hasattr(r, "score") or r.score is None:
                raise ConsensusBuilderError(f"Response at index {idx} has missing or empty score.")

        logger = logging.getLogger(__name__)

        # 2. Extract Common Concepts
        common_concepts = self.extract_common_concepts(responses)
        
        # 3. Extract Unique Contributions
        unique_contributions = self.extract_unique_contributions(responses, common_concepts)

        # 4. Compute Agreement Scores
        agreement_scores, overall_agreement = self.compute_agreement(responses)

        # 5. Evaluate Multi-factor Scores and Select Winner
        best_response = None
        best_weighted_score = -1.0
        
        provider_scores = {}
        
        for idx, r in enumerate(responses):
            provider_name = getattr(r, "provider_name", None) or r.model
            
            # 5a. Prompt Score
            prompt_score = 0.0
            if r.score:
                if r.score.overall_score is not None:
                    prompt_score = r.score.overall_score
                else:
                    try:
                        prompt_score = r.calculate_overall_score()
                    except Exception:
                        prompt_score = 0.0
            
            # 5b. Agreement Score
            agreement = agreement_scores.get(idx, 0.0)
            
            # 5c. Learning Style Score (0-100) -> Normalized to 0-1
            learning_style_score = self.compute_learning_style_alignment(r.prompt, learning_style) / 100.0
            
            # 5d. Completeness Score (0-100) -> Normalized to 0-1
            completeness_score = self.compute_completeness(r.prompt) / 100.0
            
            # 5e. Weighted Final Score
            weighted_score = (0.4 * prompt_score) + (0.3 * agreement) + (0.2 * learning_style_score) + (0.1 * completeness_score)
            
            provider_scores[provider_name] = {
                "prompt_score": prompt_score,
                "agreement_score": agreement,
                "learning_style_score": learning_style_score * 100,
                "completeness_score": completeness_score * 100,
                "weighted_score": weighted_score
            }
            
            logger.debug(f"Provider {provider_name} scores -> Prompt: {prompt_score:.2f}, Agreement: {agreement:.2f}, Learning: {learning_style_score:.2f}, Completeness: {completeness_score:.2f}, Weighted: {weighted_score:.2f}")

            # Select best
            if weighted_score > best_weighted_score:
                best_weighted_score = weighted_score
                best_response = r
                
        if not best_response:
            raise ConsensusBuilderError("Could not determine best response from the list.")

        winner_provider = getattr(best_response, "provider_name", None) or best_response.model
        winner_scores = provider_scores[winner_provider]
        
        # 6. Consensus Synthesis
        synthesized_prompt = self.synthesize_final_prompt(best_response, unique_contributions)
        
        # Other existing fields
        combined_strengths = self.aggregate_strengths(responses)
        consensus_reasoning = self.generate_consensus_reasoning(responses, best_response, combined_strengths)
        contributors = self.extract_contributors(responses)

        logger.info(f"Selected winner: {winner_provider} with weighted score {best_weighted_score:.2f}")

        # 7. Return ConsensusResult
        return ConsensusResult(
            request_id=request_id,
            final_prompt=synthesized_prompt,
            consensus_reasoning=consensus_reasoning,
            combined_strengths=combined_strengths,
            quality_score=best_weighted_score,  # Using weighted score as quality_score for backward compatibility
            contributors=contributors,
            response_count=len(responses),
            winner_provider=winner_provider,
            winner_model=best_response.model,
            prompt_score=winner_scores["prompt_score"],
            agreement_score=winner_scores["agreement_score"],
            learning_style_score=winner_scores["learning_style_score"],
            completeness_score=winner_scores["completeness_score"],
            overall_consensus_score=best_weighted_score,
            common_concepts=common_concepts,
            unique_contributions=unique_contributions,
            providers_used=contributors,
            failed_providers=failed_providers,
            response_metadata={
                "best_model": winner_provider,
                "best_role": best_response.role,
                "contributors_count": len(contributors),
                "overall_agreement": overall_agreement
            }
        )

    def extract_common_concepts(self, responses: list[CouncilResponse]) -> list[str]:
        """Identify concepts that appear in multiple responses based on reasoning and strengths."""
        if len(responses) < 2:
            return []
            
        all_words = []
        for r in responses:
            text = (r.reasoning + " " + " ".join(r.strengths)).lower()
            # Simple word extraction
            words = set(re.findall(r'\b[a-z]{5,}\b', text)) # Only consider words > 4 chars
            all_words.append(words)
            
        # Find words that appear in at least 2 responses
        word_counts = {}
        for word_set in all_words:
            for word in word_set:
                word_counts[word] = word_counts.get(word, 0) + 1
                
        common = [word for word, count in word_counts.items() if count >= 2]
        
        # Filter out common stop words if any (basic list)
        stop_words = {"which", "their", "there", "about", "would", "these", "other", "using"}
        common = [w for w in common if w not in stop_words]
        
        return sorted(common)[:10] # Return top 10 common concepts

    def extract_unique_contributions(self, responses: list[CouncilResponse], common_concepts: list[str]) -> Dict[str, list[str]]:
        """Identify unique educational contributions for every provider."""
        unique_contributions = {}
        
        # We can look at strengths for unique contributions
        for r in responses:
            provider = getattr(r, "provider_name", None) or r.model
            unique_strengths = []
            
            for strength in r.strengths:
                strength_lower = strength.lower()
                # If the strength doesn't contain a lot of common concept words, it's more unique
                overlap = sum(1 for concept in common_concepts if concept in strength_lower)
                if overlap < 2:
                    unique_strengths.append(strength)
            
            # If all were somehow common, just take the first one
            if not unique_strengths and r.strengths:
                unique_strengths.append(r.strengths[0])
                
            unique_contributions[provider] = unique_strengths[:3] # Limit to top 3
            
        return unique_contributions

    def compute_agreement(self, responses: list[CouncilResponse]) -> tuple[Dict[int, float], float]:
        """Compute pairwise agreement scores based on prompt text similarity."""
        n = len(responses)
        if n == 0:
            return {}, 0.0
        if n == 1:
            return {0: 1.0}, 1.0
            
        scores = {i: 0.0 for i in range(n)}
        total_similarity = 0.0
        pairs = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                text_i = responses[i].prompt[:2000] # Limit length for performance
                text_j = responses[j].prompt[:2000]
                
                # Use difflib for local text similarity
                similarity = difflib.SequenceMatcher(None, text_i, text_j).ratio()
                
                scores[i] += similarity
                scores[j] += similarity
                total_similarity += similarity
                pairs += 1
                
        # Average per response
        for i in range(n):
            scores[i] = scores[i] / (n - 1)
            
        overall_agreement = total_similarity / pairs if pairs > 0 else 0.0
        
        return scores, overall_agreement

    def compute_learning_style_alignment(self, prompt: str, learning_style: str) -> float:
        """Evaluate how well the response satisfies the requested learning style. Returns 0-100."""
        prompt_lower = prompt.lower()
        score = 50.0 # Base score
        
        style = learning_style.lower()
        keywords = []
        
        if "visual" in style:
            keywords = ["diagram", "chart", "visualize", "picture", "imagine", "see", "flowchart", "table", "map"]
        elif "hand" in style or "kinesthetic" in style:
            keywords = ["practice", "exercise", "build", "create", "activity", "project", "hands-on", "try", "do"]
        elif "read" in style or "write" in style:
            keywords = ["read", "write", "summarize", "definition", "structure", "list", "explain", "text", "notes"]
        elif "audit" in style or "listen" in style:
            keywords = ["discuss", "listen", "explain aloud", "tell", "story", "podcast", "debate", "verbal"]
            
        # Count hits
        hits = sum(1 for kw in keywords if kw in prompt_lower)
        
        if hits >= 3:
            score = 100.0
        elif hits == 2:
            score = 85.0
        elif hits == 1:
            score = 70.0
            
        return score

    def compute_completeness(self, prompt: str) -> float:
        """Evaluate whether the response contains standard educational components. Returns 0-100."""
        prompt_lower = prompt.lower()
        components_found = 0
        
        # Basic heuristic checks
        if "introduction" in prompt_lower or "overview" in prompt_lower or "welcome" in prompt_lower:
            components_found += 1
            
        # Explanation usually has paragraphs or steps
        if len(prompt.split("\n\n")) > 3:
            components_found += 1
            
        if "example" in prompt_lower or "for instance" in prompt_lower:
            components_found += 1
            
        if "summary" in prompt_lower or "in conclusion" in prompt_lower or "recap" in prompt_lower:
            components_found += 1
            
        if "practice" in prompt_lower or "exercise" in prompt_lower or "activity" in prompt_lower or "quiz" in prompt_lower:
            components_found += 1
            
        if "conclusion" in prompt_lower or "wrap-up" in prompt_lower or "next steps" in prompt_lower:
            components_found += 1
            
        score = (components_found / 6.0) * 100
        return min(100.0, max(0.0, score))

    def synthesize_final_prompt(self, winner: CouncilResponse, unique_contributions: Dict[str, list[str]]) -> str:
        """Merge strongest explanations and ideas into the winner's prompt."""
        final_prompt = winner.prompt
        
        winner_provider = getattr(winner, "provider_name", None) or winner.model
        
        # Check if other providers had unique contributions
        additions = []
        for provider, contributions in unique_contributions.items():
            if provider != winner_provider and contributions:
                additions.append(f"- From {provider}: {', '.join(contributions)}")
                
        if additions:
            final_prompt += "\n\n---\n### Consensus Additions\n*The AI Council also recommends incorporating the following ideas:*\n"
            final_prompt += "\n".join(additions)
            
        return final_prompt

    def select_best_response(self, responses: list[CouncilResponse]) -> CouncilResponse:
        """Legacy fallback: Select the best response based on overall score and provider priority tiebreaker."""
        # Kept for backward compatibility if called directly
        def get_provider_priority(model_name: str, provider_name: str = "") -> int:
            model_lower = model_name.lower()
            provider_lower = (provider_name or "").lower()
            if "gpt" in model_lower or "openai" in provider_lower:
                return 4
            elif "claude" in model_lower or "claude" in provider_lower:
                return 3
            elif "gemini" in model_lower or "gemini" in provider_lower:
                return 2
            elif "deepseek" in model_lower or "deepseek" in provider_lower:
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

            p_name = getattr(r, "provider_name", None) or ""
            priority = get_provider_priority(r.model, p_name)

            if score > best_score:
                best_score = score
                best_priority = priority
                best_response = r
            elif score == best_score:
                if priority > best_priority:
                    best_priority = priority
                    best_response = r
            
        if not best_response:
            raise ConsensusBuilderError("Could not determine best response from the list.")
        return best_response

    def aggregate_strengths(self, responses: list[CouncilResponse]) -> list[str]:
        """Collect and deduplicate strengths from all responses."""
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
        """Generate a text summary explaining consensus contributions."""
        has_gpt = False
        has_claude = False
        has_gemini = False
        has_deepseek = False

        for r in responses:
            model_lower = r.model.lower()
            provider_name = getattr(r, "provider_name", None) or ""
            provider_lower = provider_name.lower()
            
            if "gpt" in model_lower or "groq" in model_lower or "llama" in model_lower or "openai" in provider_lower or "groq" in provider_lower or "openrouter" in provider_lower or "cerebras" in provider_lower or "sambanova" in provider_lower:
                has_gpt = True
            elif "claude" in model_lower or "claude" in provider_lower:
                has_claude = True
            elif "gemini" in model_lower or "gemini" in provider_lower:
                has_gemini = True
            elif "deepseek" in model_lower or "deepseek" in provider_lower:
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
        """Legacy fallback: Average all overall scores and round to 2 decimal places."""
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
            name_to_use = getattr(r, "provider_name", None)
            if not name_to_use:
                name_to_use = r.model
                
            if name_to_use:
                name_to_use = name_to_use.lower()
                if name_to_use not in contributors:
                    contributors.append(name_to_use)
        return contributors
