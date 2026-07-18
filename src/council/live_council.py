"""
LiveCouncil - Phase 20.5

Orchestrates the entire Multi-Provider Live Council workflow:
1. Executes active providers in parallel using CouncilExecutor
2. Standardizes/normalizes responses
3. Builds consensus using ConsensusBuilder
4. Scores the consensus prompt using PromptScorer
5. Generates explaining details using ExplanationGenerator
6. Returns structured council result
"""

import logging
from typing import Any, Dict, List, Optional

from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse
from src.models.consensus_result import ConsensusResult
from src.scoring.prompt_scorer import PromptScorer, ResponseScore, PromptScoringError
from src.consensus.consensus_builder import ConsensusBuilder, ConsensusBuilderError
from src.explanation.explanation_generator import ExplanationGenerator, ExplanationGenerationError
from src.council.council_executor import CouncilExecutor, CouncilExecutionError
from src.providers.provider_registry import ProviderRegistry
from src.council.council_cache import council_cache

logger = logging.getLogger("aithera.live_council")


class LiveCouncilError(Exception):
    """Exception raised when the live council workflow fails critically."""
    def __init__(self, message: str, error_details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_details = error_details or {}

class LiveCouncil:
    """Live Council Service that runs the complete AI Council workflow."""

    def __init__(
        self,
        provider_registry: Optional[ProviderRegistry] = None,
        council_executor: Optional[CouncilExecutor] = None,
        consensus_builder: Optional[ConsensusBuilder] = None,
        prompt_scorer: Optional[PromptScorer] = None,
        explanation_generator: Optional[ExplanationGenerator] = None,
    ) -> None:
        """Initialize the LiveCouncil service.
        
        Args:
            provider_registry: Optional registry for providers.
            council_executor: Optional executor for parallel execution.
            consensus_builder: Optional builder for consensus generation.
            prompt_scorer: Optional scorer for evaluation.
            explanation_generator: Optional generator for descriptions.
        """
        self.provider_registry = provider_registry or ProviderRegistry()
        self.council_executor = council_executor or CouncilExecutor(
            provider_registry=self.provider_registry
        )
        self.consensus_builder = consensus_builder or ConsensusBuilder()
        self.prompt_scorer = prompt_scorer or PromptScorer()
        self.explanation_generator = explanation_generator or ExplanationGenerator()

    async def execute(self, request: PromptRequest, timeout: float = 300.0) -> Dict[str, Any]:
        """Execute the complete live council workflow for the given PromptRequest.
        
        Args:
            request: The PromptRequest object.
            
        Returns:
            Dict[str, Any]: The final structured council result with keys:
                - responses: List of CouncilResponse
                - consensus: ConsensusResult
                - score: ResponseScore
                - explanation: Dict[str, Any]
                - contributors: List[str]
                
        Raises:
            LiveCouncilError: If any step fails critically.
        """
        logger.info("Executing Live Council for request ID: %s", getattr(request, "id", None))
        
        # Check cache
        cached_result = council_cache.get(request)
        if cached_result:
            logger.info("Live Council returning cached result for request ID: %s", getattr(request, "id", None))
            # Tag the consensus result as a cache hit
            if "consensus" in cached_result:
                cached_result["consensus"].cache_hit = True
            return cached_result
        
        import time
        start_time = time.time()
        
        # Step 1 & 2: Execute providers & normalize responses
        try:
            logger.info("Before council execution")
            responses = await self.council_executor.execute_council(request, timeout=timeout)
            logger.info("After council execution")
        except CouncilExecutionError as e:
            logger.error("Provider execution failed during live council: %s", e)
            raise LiveCouncilError(f"Live Council execution failed: {e}", getattr(e, "error_details", {})) from e
        except Exception as e:
            logger.error("Unexpected error in provider execution: %s", e)
            raise LiveCouncilError(f"Unexpected execution error: {e}") from e

        # Step 3: Build consensus
        request_id = getattr(request, "id", 0) or 0
        try:
            logger.info("Before consensus generation")
            consensus_result = self.consensus_builder.build_consensus(
                responses=responses,
                request_id=request_id,
                learning_style=request.learning_style,
                failed_providers=getattr(self.council_executor, "failed_providers", [])
            )
            logger.info("After consensus generation")
        except ConsensusBuilderError as e:
            logger.error("Consensus building failed: %s", e)
            raise LiveCouncilError(f"Consensus building failed: {e}") from e
        except Exception as e:
            logger.error("Unexpected error in consensus builder: %s", e)
            raise LiveCouncilError(f"Unexpected consensus building error: {e}") from e

        # Step 4: Score consensus prompt
        try:
            score = self.prompt_scorer.score_prompt(
                consensus_result=consensus_result,
                learning_style=request.learning_style
            )
        except PromptScoringError as e:
            logger.error("Prompt scoring failed: %s", e)
            raise LiveCouncilError(f"Prompt scoring failed: {e}") from e
        except Exception as e:
            logger.error("Unexpected error in prompt scorer: %s", e)
            raise LiveCouncilError(f"Unexpected prompt scoring error: {e}") from e

        # Step 5: Generate explanation details
        try:
            explanation = self.explanation_generator.generate_full_explanation(
                consensus_result=consensus_result,
                score=score,
                learning_style=request.learning_style
            )
        except ExplanationGenerationError as e:
            logger.error("Explanation generation failed: %s", e)
            raise LiveCouncilError(f"Explanation generation failed: {e}") from e
        except Exception as e:
            logger.error("Unexpected error in explanation generator: %s", e)
            raise LiveCouncilError(f"Unexpected explanation generation error: {e}") from e

        # Calculate Phase 4 Metrics
        end_time = time.time()
        total_exec_time = end_time - start_time
        
        provider_times = {}
        max_provider_time = 0.0
        for r in responses:
            p_time = r.metadata.response_time if r.metadata and r.metadata.response_time else 0.0
            provider_times[r.provider_name] = p_time
            if p_time > max_provider_time:
                max_provider_time = p_time
                
        parallel_efficiency = (max_provider_time / total_exec_time) if total_exec_time > 0 else 1.0
        
        consensus_result.execution_time = total_exec_time
        consensus_result.provider_execution_times = provider_times
        consensus_result.parallel_efficiency = parallel_efficiency
        consensus_result.retry_stats = {} # Add logic in executor if tracking retries

        # Step 6: Return final result
        result = {
            "responses": responses,
            "consensus": consensus_result,
            "score": score,
            "explanation": explanation,
            "contributors": consensus_result.contributors,
            "failed_providers": getattr(self.council_executor, "failed_providers", []),
            "error_details": getattr(self.council_executor, "error_details", {})
        }
        
        # Save to cache
        council_cache.set(request, result)
        
        # Tag cache_hit=False for the fresh result
        consensus_result.cache_hit = False
        
        logger.info(
            "Live Council workflow completed successfully for request ID: %s",
            request_id
        )
        return result
