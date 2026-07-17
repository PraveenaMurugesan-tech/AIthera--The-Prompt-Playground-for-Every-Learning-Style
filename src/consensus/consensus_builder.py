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
                        
            # 5c. Learning Style Score (0-100) -> Normalized to 0-1
            learning_style_score = self.compute_learning_style_alignment(r.prompt, learning_style) / 100.0
            
            # 5d. Completeness Score (0-100) -> Normalized to 0-1
            completeness_score = self.compute_completeness(r.prompt) / 100.0
            
            # Fallback if prompt_score is 0 (since it hasn't been evaluated by LLM yet)
            if prompt_score == 0.0:
                prompt_score = (learning_style_score + completeness_score) / 2.0
                
            # 5b. Agreement Score
            agreement = agreement_scores.get(idx, 0.0)
            
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
        consensus_reasoning = self.generate_consensus_reasoning(responses)
        contributors = self.extract_contributors(responses)
        
        # Phase 3 Fields
        scaled_agreement = overall_agreement * 100.0
        diversity_score, diversity_level = self.compute_diversity_score(scaled_agreement)
        conflicting_concepts = self.extract_conflicting_concepts(responses)
        provider_categories = self.extract_provider_contributions_categories(responses)
        coverage_score, educational_sections = self.analyze_coverage(synthesized_prompt)
        learning_style_verification = self.verify_learning_style(synthesized_prompt, learning_style)
        
        num_successful = len(contributors)
        total_providers_attempted = num_successful + len(failed_providers) if failed_providers else num_successful
        
        confidence_score = self.calculate_confidence_score(
            prompt_score=winner_scores["prompt_score"],
            agreement=overall_agreement,
            completeness=winner_scores["completeness_score"] / 100.0,
            num_successful=num_successful,
            total_providers=total_providers_attempted
        )
        
        confidence_level = self.determine_confidence_level(confidence_score)
        explanation = self.generate_explanation(
            winner_provider, provider_categories, conflicting_concepts, scaled_agreement, num_successful
        )
        evaluation_summary = self.generate_evaluation_summary(
            confidence_level, coverage_score, scaled_agreement, conflicting_concepts
        )

        logger.info(f"Selected winner: {winner_provider} with weighted score {best_weighted_score:.2f}, Confidence: {confidence_score:.2f}")

        # 7. Return ConsensusResult
        return ConsensusResult(
            request_id=request_id,
            final_prompt=synthesized_prompt, # Keep for backward compatibility
            consensus_reasoning=consensus_reasoning, # Keep for backward compatibility
            combined_strengths=combined_strengths, # Keep for backward compatibility
            quality_score=best_weighted_score,  # Using weighted score as quality_score for backward compatibility
            contributors=contributors,
            response_count=len(responses),
            winner_provider=winner_provider,
            winner_model=best_response.model,
            prompt_score=winner_scores["prompt_score"],
            agreement_score=winner_scores["agreement_score"] * 100.0,
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
            },
            # Phase 2 Fields
            confidence_score=confidence_score,
            educational_structure_score=winner_scores["completeness_score"], # Reusing completeness for structure score
            synthesized_prompt=synthesized_prompt,
            synthesized_reasoning=consensus_reasoning,
            merged_strengths=combined_strengths,
            unique_concepts=list(unique_contributions.keys()), # simplistic, we can store keys
            conflicting_concepts=conflicting_concepts,
            provider_contributions=provider_categories,
            # Phase 3 Fields
            explanation=explanation,
            diversity_score=diversity_score,
            diversity_level=diversity_level,
            coverage_score=coverage_score,
            educational_sections=educational_sections,
            learning_style_verification=learning_style_verification,
            confidence_level=confidence_level,
            evaluation_summary=evaluation_summary
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
                text_i = responses[i].prompt.lower()
                text_j = responses[j].prompt.lower()
                
                # Use word overlap (Jaccard similarity) instead of sequence matching
                words_i = set(re.findall(r'\b[a-z]{4,}\b', text_i))
                words_j = set(re.findall(r'\b[a-z]{4,}\b', text_j))
                
                if not words_i and not words_j:
                    similarity = 1.0
                elif not words_i or not words_j:
                    similarity = 0.0
                else:
                    intersection = len(words_i.intersection(words_j))
                    union = len(words_i.union(words_j))
                    # Scale up slightly as Jaccard can still be low for diverse vocab
                    similarity = min(1.0, (intersection / union) * 1.5)

                
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
            keywords = ["diagram", "chart", "visualize", "picture", "imagine", "see", "flowchart", "table", "map", "graph"]
        elif "hand" in style or "kinesthetic" in style or "step" in style:
            keywords = ["practice", "exercise", "build", "create", "activity", "project", "hands-on", "try", "do", "step", "experiment"]
        elif "read" in style or "write" in style or "theoretical" in style or "research" in style:
            keywords = ["read", "write", "summarize", "definition", "structure", "list", "explain", "text", "notes", "theory", "concept"]
        elif "audit" in style or "listen" in style or "story" in style or "conversational" in style:
            keywords = ["discuss", "listen", "explain aloud", "tell", "story", "podcast", "debate", "verbal", "analogy", "imagine if"]
            
        # Count hits
        hits = sum(1 for kw in keywords if kw in prompt_lower)
        
        if hits >= 4:
            score = 100.0
        elif hits == 3:
            score = 90.0
        elif hits == 2:
            score = 75.0
        elif hits == 1:
            score = 60.0
            
        return score

    def compute_completeness(self, prompt: str) -> float:
        """Evaluate whether the response contains standard educational components. Returns 0-100."""
        return self.compute_structure_score(prompt)

    def compute_structure_score(self, prompt: str) -> float:
        """Evaluate for: intro, explanation, examples, exercises, summary, learning objs, real-world apps. Returns 0-100."""
        prompt_lower = prompt.lower()
        components_found = 0
        total_components = 7
        
        # 1. Intro / Welcome
        if any(kw in prompt_lower for kw in ["introduction", "overview", "welcome", "in this lesson"]):
            components_found += 1
            
        # 2. Explanation / Core Concept
        if len(prompt.split("\n\n")) > 3 or "concept" in prompt_lower or "definition" in prompt_lower:
            components_found += 1
            
        # 3. Examples
        if any(kw in prompt_lower for kw in ["example", "for instance", "e.g.", "such as"]):
            components_found += 1
            
        # 4. Exercises / Practice
        if any(kw in prompt_lower for kw in ["practice", "exercise", "activity", "quiz", "try it"]):
            components_found += 1
            
        # 5. Summary / Wrap-up
        if any(kw in prompt_lower for kw in ["summary", "in conclusion", "recap", "wrap-up"]):
            components_found += 1
            
        # 6. Learning Objectives
        if any(kw in prompt_lower for kw in ["objective", "goal", "by the end of", "you will learn"]):
            components_found += 1
            
        # 7. Real-world applications
        if any(kw in prompt_lower for kw in ["real-world", "real world", "application", "use case", "in practice"]):
            components_found += 1
            
        score = (components_found / float(total_components)) * 100
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
        """Collect and deduplicate strengths from all responses, normalizing capitalization."""
        seen = set()
        combined_strengths = []
        for r in responses:
            for strength in r.strengths:
                if strength and isinstance(strength, str):
                    stripped = strength.strip()
                    if not stripped:
                        continue
                    # Normalize capitalization (capitalize first letter)
                    normalized = stripped[0].upper() + stripped[1:]
                    lower_check = normalized.lower()
                    if lower_check not in seen:
                        seen.add(lower_check)
                        combined_strengths.append(normalized)
        
        # Keep most meaningful (longest/most detailed first) up to 10
        combined_strengths.sort(key=len, reverse=True)
        return combined_strengths[:10]

    def generate_consensus_reasoning(
        self,
        responses: list[CouncilResponse]
    ) -> str:
        """Group similar reasoning from all responses, preserving unique insights."""
        all_sentences = []
        for r in responses:
            if r.reasoning:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', r.reasoning) if s.strip()]
                all_sentences.extend(sentences)
                
        seen = set()
        unique_reasoning = []
        for s in all_sentences:
            s_lower = s.lower()
            # Simple deduplication
            if not any(difflib.SequenceMatcher(None, s_lower, seen_s).ratio() > 0.8 for seen_s in seen):
                seen.add(s_lower)
                unique_reasoning.append(s)
                
        if not unique_reasoning:
            return "Participating council providers contributed to the prompt construction."
            
        return " ".join(unique_reasoning[:5]) # Limit to top 5 sentences for clarity

    def calculate_confidence_score(
        self,
        prompt_score: float,
        agreement: float,
        completeness: float,
        num_successful: int,
        total_providers: int
    ) -> float:
        """Calculate a 0-100 confidence score based on multiple metrics."""
        # Weighted combination
        # Prompt Quality: 40%
        # Agreement: 30%
        # Completeness: 20%
        # Provider Success Ratio: 10%
        
        success_ratio = (num_successful / total_providers) if total_providers > 0 else 0.0
        
        confidence = (
            (prompt_score * 100 * 0.40) +
            (agreement * 100 * 0.30) +
            (completeness * 100 * 0.20) +
            (success_ratio * 100 * 0.10)
        )
        return min(100.0, max(0.0, confidence))

    def extract_conflicting_concepts(self, responses: list[CouncilResponse]) -> list[str]:
        """Detect conflicting recommendations between providers (e.g. negations)."""
        conflicts = []
        # Basic heuristic: look for "avoid", "don't", "not" near keywords in one, and the keyword in another
        keywords = ["visuals", "code", "theory", "examples", "exercises", "math", "story", "recursion", "iteration"]
        
        for kw in keywords:
            supported = False
            opposed = False
            for r in responses:
                text = (r.prompt + " " + r.reasoning).lower()
                if f"no {kw}" in text or f"avoid {kw}" in text or f"don't use {kw}" in text:
                    opposed = True
                elif kw in text:
                    supported = True
                    
            if supported and opposed:
                conflicts.append(kw)
                
        return conflicts

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

    # Phase 3 Enhancements
    def compute_diversity_score(self, agreement_score: float) -> tuple[float, str]:
        """Compute diversity score (0-100) and level based on overall agreement."""
        diversity_score = max(0.0, 100.0 - agreement_score)
        if diversity_score >= 66:
            level = "High"
        elif diversity_score >= 33:
            level = "Medium"
        else:
            level = "Low"
        return round(diversity_score, 2), level

    def extract_provider_contributions_categories(self, responses: list[CouncilResponse]) -> Dict[str, list[str]]:
        contributions = {}
        categories = {
            "Introduction": ["introduction", "overview", "welcome", "begin"],
            "Explanation": ["concept", "definition", "explain", "theory", "core"],
            "Examples": ["example", "for instance", "such as", "demonstrate"],
            "Practice": ["practice", "try it", "hands-on"],
            "Exercises": ["exercise", "quiz", "test", "question"],
            "Summary": ["summary", "conclusion", "recap", "wrap-up"],
            "Tips": ["tip", "hint", "remember", "note", "best practice"],
            "Visual aids": ["diagram", "chart", "visualize", "picture", "graph"],
            "Analogies": ["analogy", "like a", "imagine", "similar to"],
            "Real-world applications": ["real-world", "application", "in practice", "use case"]
        }
        for r in responses:
            provider = getattr(r, "provider_name", None) or r.model
            text = (r.prompt + " " + r.reasoning).lower()
            provider_cats = []
            for cat, keywords in categories.items():
                if any(kw in text for kw in keywords):
                    provider_cats.append(cat)
            contributions[provider] = provider_cats
        return contributions

    def analyze_coverage(self, prompt: str) -> tuple[float, Dict[str, bool]]:
        prompt_lower = prompt.lower()
        sections = {
            "Introduction": any(kw in prompt_lower for kw in ["introduction", "overview", "welcome", "in this lesson"]),
            "Explanation": len(prompt.split("\n\n")) > 3 or "concept" in prompt_lower or "definition" in prompt_lower,
            "Examples": any(kw in prompt_lower for kw in ["example", "for instance", "e.g.", "such as"]),
            "Practice": any(kw in prompt_lower for kw in ["practice", "activity", "try it"]),
            "Exercises": any(kw in prompt_lower for kw in ["exercise", "quiz", "test"]),
            "Summary": any(kw in prompt_lower for kw in ["summary", "in conclusion", "recap", "wrap-up"]),
            "Tips": any(kw in prompt_lower for kw in ["tip", "hint", "best practice"])
        }
        components_found = sum(sections.values())
        total_components = len(sections)
        coverage_score = (components_found / float(total_components)) * 100.0 if total_components > 0 else 0.0
        return round(coverage_score, 2), sections

    def verify_learning_style(self, prompt: str, requested_style: str) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        score = self.compute_learning_style_alignment(prompt, requested_style)
        
        styles = {
            "visual": ["diagram", "chart", "visualize", "picture", "imagine", "see", "flowchart", "table", "map", "graph"],
            "kinesthetic": ["practice", "exercise", "build", "create", "activity", "project", "hands-on", "try", "do", "step", "experiment"],
            "reading": ["read", "write", "summarize", "definition", "structure", "list", "explain", "text", "notes", "theory", "concept"],
            "auditory": ["discuss", "listen", "explain aloud", "tell", "story", "podcast", "debate", "verbal", "analogy", "imagine if"]
        }
        
        max_hits = -1
        detected_style = "unknown"
        for style, keywords in styles.items():
            hits = sum(1 for kw in keywords if kw in prompt_lower)
            if hits > max_hits:
                max_hits = hits
                detected_style = style
                
        return {
            "requested": requested_style.capitalize(),
            "detected": detected_style.capitalize(),
            "confidence": score
        }

    def determine_confidence_level(self, confidence_score: float) -> str:
        if confidence_score >= 80:
            return "High"
        elif confidence_score >= 50:
            return "Medium"
        return "Low"

    def generate_explanation(
        self, 
        winner_provider: str, 
        provider_contributions: Dict[str, list[str]], 
        conflicting_concepts: list[str], 
        agreement_score: float,
        num_successful: int
    ) -> str:
        if num_successful == 1:
            return f"The council selected {winner_provider}'s response as it was the only successful provider."
            
        explanation = f"The council selected {winner_provider}'s educational structure because multiple providers agreed on the learning sequence."
        
        if agreement_score < 40 or conflicting_concepts:
            explanation = f"While providers disagreed on some concepts like {', '.join(conflicting_concepts) if conflicting_concepts else 'general structure'}, the council ultimately selected {winner_provider}'s approach as the most balanced."
            
        contrib_texts = []
        for p, contribs in provider_contributions.items():
            if p != winner_provider and contribs:
                contrib_texts.append(f"{p} contributed {', '.join(contribs).lower()}.")
                
        if contrib_texts:
            explanation += " " + " ".join(contrib_texts)
            
        return explanation

    def generate_evaluation_summary(
        self, 
        confidence_level: str, 
        coverage_score: float, 
        agreement_score: float, 
        conflicting_concepts: list[str]
    ) -> str:
        summary = f"{confidence_level} confidence consensus."
        
        if coverage_score >= 80:
            summary += " Excellent educational coverage."
        elif coverage_score >= 50:
            summary += " Adequate educational coverage."
        else:
            summary += " Poor educational coverage."
            
        if agreement_score >= 70:
            summary += " Providers strongly agreed."
        elif agreement_score >= 40:
            summary += " Providers partially agreed."
        else:
            summary += " Providers disagreed."
            
        if conflicting_concepts:
            summary += " Major conflicts detected."
        else:
            summary += " No major conflicts detected."
            
        return summary

