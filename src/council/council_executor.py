"""
CouncilExecutor - Phase 15

Orchestrates the AI Council workflow by coordinating multiple AI providers.

Responsibilities:
- Accept a PromptRequest input
- Retrieve learning style profile from LearningStyleEngine
- Load and inject variables into prompt templates
- Orchestrate concurrent execution of all providers
- Normalize responses using ResponseNormalizer
- Handle partial and complete provider failures
- Return structured execution results with metadata
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.models.prompt_request import PromptRequest
from src.models.council_response import CouncilResponse
from src.council.response_normalizer import ResponseNormalizer, NormalizationError
from src.learning.style_engine import LearningStyleEngine, InvalidLearningStyleError
from src.providers.base_provider import BaseProvider, ProviderConfig
from src.providers.groq_client import GroqClient
from src.providers.claude_client import ClaudeClient
from src.providers.gemini_client import GeminiClient
from src.providers.deepseek_client import DeepSeekClient
from src.providers.openrouter_client import OpenRouterClient
from src.providers.cerebras_client import CerebrasClient
from src.providers.sambanova_client import SambaNovaClient
from src.providers.provider_registry import ProviderRegistry
from src.providers.provider_health import ProviderHealthTracker
from src.workflow.task_profiles import TaskProfileRegistry
from src.workflow.schemas import UniversalInput, DetectedIntent

# Configure logging
logger = logging.getLogger("aithera.council_executor")


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class CouncilExecutionError(Exception):
    """Exception raised when council execution fails critically.
    
    Raised when:
    - All providers fail
    - Prompt template cannot be loaded
    - Invalid request data
    """
    def __init__(self, message: str, error_details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_details = error_details or {}


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class CouncilExecutionResult:
    """Result of a council execution containing all responses and metadata.
    
    Attributes:
        responses: List of successful CouncilResponse objects from providers
        successful_providers: List of provider names that executed successfully
        failed_providers: List of provider names that failed
        execution_time: Total execution time in seconds
        error_details: Dictionary containing error messages for failed providers
    """
    responses: List[CouncilResponse] = field(default_factory=list)
    successful_providers: List[str] = field(default_factory=list)
    failed_providers: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    error_details: Dict[str, str] = field(default_factory=dict)

    def get_successful_count(self) -> int:
        """Return count of successful provider responses."""
        return len(self.successful_providers)

    def get_failed_count(self) -> int:
        """Return count of failed providers."""
        return len(self.failed_providers)

    def is_complete_success(self) -> bool:
        """Check if all providers succeeded."""
        return self.get_failed_count() == 0

    def is_partial_success(self) -> bool:
        """Check if at least one provider succeeded."""
        return self.get_successful_count() > 0


# ============================================================================
# COUNCIL EXECUTOR
# ============================================================================

class CouncilExecutor:
    """Orchestrates the AI Council workflow.
    
    The CouncilExecutor coordinates multiple AI providers to generate educational
    prompts. It handles template loading, variable substitution, concurrent
    execution, response normalization, and error handling.
    
    Attributes:
        learning_style_engine: Engine for retrieving learning style profiles
        response_normalizer: Normalizer for standardizing provider responses
        prompts_dir: Path to the prompts directory containing template files
    
    Example:
        >>> executor = CouncilExecutor()
        >>> request = PromptRequest(
        ...     topic="Photosynthesis",
        ...     objective="Understand the light reactions",
        ...     learning_style="visual",
        ...     difficulty="intermediate",
        ...     education_level="high_school",
        ...     output_length="moderate"
        ... )
        >>> result = await executor.execute(request)
    """

    # Provider templates mapping
    PROVIDER_TEMPLATES = {
        "groq": "gpt_teacher.txt",
        "claude": "claude_reasoning.txt",
        "gemini": "gemini_visual.txt",
        "deepseek": "deepseek_logic.txt",
        "openrouter": "gpt_teacher.txt",
        "cerebras": "gpt_teacher.txt",
        "sambanova": "gpt_teacher.txt",
    }

    def __init__(
        self,
        prompts_dir: Optional[Path] = None,
        style_engine: Optional[LearningStyleEngine] = None,
        response_normalizer: Optional[ResponseNormalizer] = None,
        provider_registry: Optional[ProviderRegistry] = None,
        health_tracker: Optional[ProviderHealthTracker] = None,
    ) -> None:
        """Initialize the CouncilExecutor.
        
        Args:
            prompts_dir: Path to the prompts directory. Defaults to src/../prompts
            style_engine: LearningStyleEngine instance. Creates new if not provided
            response_normalizer: ResponseNormalizer instance. Creates new if not provided
            provider_registry: ProviderRegistry instance. Creates new if not provided
            health_tracker: ProviderHealthTracker instance. Creates new if not provided
        """
        self.learning_style_engine = style_engine or LearningStyleEngine()
        self.response_normalizer = response_normalizer or ResponseNormalizer()
        self.provider_registry = provider_registry or ProviderRegistry()
        self.health_tracker = health_tracker or ProviderHealthTracker()

        # Track failed and successful providers across executions
        self.failed_providers: List[str] = []
        self.successful_providers: List[str] = []

        # Resolve prompts directory
        if prompts_dir is None:
            # Assume we're in src/council, so go up to project root then to prompts
            self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        else:
            self.prompts_dir = prompts_dir

        # Verify prompts directory exists
        if not self.prompts_dir.exists():
            raise CouncilExecutionError(
                f"Prompts directory not found at {self.prompts_dir}"
            )

        logger.info("CouncilExecutor initialized with prompts_dir: %s", self.prompts_dir)

    def load_template(self, template_filename: str) -> str:
        """Load a prompt template from the prompts directory.
        
        Args:
            template_filename: Name of the template file (e.g., "gpt_teacher.txt")
            
        Returns:
            str: Template content
            
        Raises:
            CouncilExecutionError: If template cannot be loaded
        """
        template_path = self.prompts_dir / template_filename
        try:
            if not template_path.exists():
                raise CouncilExecutionError(
                    f"Template file not found: {template_path}"
                )
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if not content or not content.strip():
                raise CouncilExecutionError(
                    f"Template file is empty: {template_path}"
                )
            
            logger.debug("Loaded template: %s", template_filename)
            return content
        except CouncilExecutionError:
            raise
        except Exception as e:
            raise CouncilExecutionError(
                f"Failed to load template {template_filename}: {str(e)}"
            )

    def substitute_template_variables(
        self,
        template: str,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
        bloom_level: str = "understand",
    ) -> str:
        """Inject template variables into a prompt template.
        
        Args:
            template: The template string with {variable} placeholders
            topic: The topic of study
            objective: The pedagogical objective
            learning_style: The target learning style
            difficulty: The difficulty level
            education_level: The education level
            output_length: The requested output length
            bloom_level: The target Bloom's taxonomy level
            
        Returns:
            str: The template with all variables substituted
            
        Raises:
            CouncilExecutionError: If substitution fails
        """
        try:
            variables = {
                "topic": topic,
                "objective": objective,
                "learning_style": learning_style,
                "difficulty": difficulty,
                "education_level": education_level,
                "output_length": output_length,
                "bloom_level": bloom_level,
            }
            
            # Validate all variables are non-empty
            for var_name, var_value in variables.items():
                if not var_value or not str(var_value).strip():
                    raise CouncilExecutionError(
                        f"Template variable '{var_name}' is empty or None"
                    )
            
            substituted = template.format(**variables)
            logger.debug("Template variables substituted successfully")
            return substituted
        except KeyError as e:
            raise CouncilExecutionError(f"Missing template variable: {str(e)}")
        except CouncilExecutionError:
            raise
        except Exception as e:
            raise CouncilExecutionError(f"Template substitution failed: {str(e)}")

    def build_provider_prompt(
        self,
        provider_name: str,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
    ) -> str:
        """Build a provider-specific prompt from template and variables.
        
        Args:
            provider_name: Name of the provider (openai, claude, gemini, deepseek)
            topic: The topic of study
            objective: The pedagogical objective
            learning_style: The target learning style
            difficulty: The difficulty level
            education_level: The education level
            output_length: The requested output length
            
        Returns:
            str: The fully-substituted provider-specific prompt
            
        Raises:
            CouncilExecutionError: If template loading or substitution fails
        """
        template_name = self.PROVIDER_TEMPLATES.get(provider_name.lower())
        if not template_name:
            raise CouncilExecutionError(
                f"Unknown provider: {provider_name}. "
                f"Supported providers: {', '.join(self.PROVIDER_TEMPLATES.keys())}"
            )
        
        template = self.load_template(template_name)
        prompt = self.substitute_template_variables(
            template,
            topic=topic,
            objective=objective,
            learning_style=learning_style,
            difficulty=difficulty,
            education_level=education_level,
            output_length=output_length,
        )
        
        logger.debug("Built prompt for provider: %s", provider_name)
        return prompt

    def _validate_request(self, request: PromptRequest) -> None:
        """Validate that a PromptRequest has all required fields.
        
        Args:
            request: The PromptRequest to validate
            
        Raises:
            CouncilExecutionError: If required fields are missing
        """
        # Universal prompts might not have educational fields
        if getattr(request, "task_type", None) != "learning" and request.topic:
            return
            
        if not request.topic or not request.objective:
            raise CouncilExecutionError(
                "PromptRequest must have topic and objective"
            )
        if not request.learning_style:
            raise CouncilExecutionError(
                "PromptRequest must have learning_style"
            )
        if not request.difficulty:
            raise CouncilExecutionError(
                "PromptRequest must have difficulty"
            )
        if not request.education_level:
            raise CouncilExecutionError(
                "PromptRequest must have education_level"
            )
        if not request.output_length:
            raise CouncilExecutionError(
                "PromptRequest must have output_length"
            )

    def _validate_learning_style(self, learning_style: str) -> None:
        """Validate that the learning style is supported.
        
        Args:
            learning_style: The learning style name
            
        Raises:
            CouncilExecutionError: If learning style is invalid
        """
        try:
            _ = self.learning_style_engine.get_style_profile(learning_style)
        except InvalidLearningStyleError as e:
            raise CouncilExecutionError(f"Invalid learning style: {str(e)}")

    async def execute_provider(
        self,
        provider: Any,  # BaseProvider subclass instance
        provider_name: str,
        topic: str,
        objective: str,
        learning_style: str,
        difficulty: str,
        education_level: str,
        output_length: str,
        bloom_level: str = "understand",
        timeout: float = 30.0,
        prompt: Optional[str] = None,
        suitability_score: Optional[float] = None,
    ) -> Optional[CouncilResponse]:
        import time
        start_time = time.time()
        
        provider_name_to_log = getattr(provider, "name", provider_name)
        
        logger.info(f"Calling provider: {provider_name_to_log}")
        try:
            logger.info(f"Before prompt generation for {provider_name_to_log}")
            response = await asyncio.wait_for(
                provider.generate_response(
                    topic=topic,
                    objective=objective,
                    learning_style=learning_style,
                    difficulty=difficulty,
                    education_level=education_level,
                    output_length=output_length,
                    bloom_level=bloom_level,
                    prompt=prompt,
                ),
                timeout=timeout
            )
            
            # Inject suitability score if we have a CouncilResponse directly
            if isinstance(response, CouncilResponse) and suitability_score is not None:
                if getattr(response, "metadata", None) is None:
                    from src.models.council_response import ResponseMetadata
                    response.metadata = ResponseMetadata()
                response.metadata.suitability_score = suitability_score
                
            logger.info(f"After prompt generation for {provider_name_to_log}")
            elapsed = time.time() - start_time
            print(f"Execution time for {provider_name_to_log}: {elapsed:.2f}s")
            return response
        except Exception:
            elapsed = time.time() - start_time
            print(f"Execution time for {provider_name_to_log}: {elapsed:.2f}s")
            logger.exception(f"{provider_name_to_log} failed")
            raise

    async def execute(
        self,
        request: PromptRequest
    ) -> CouncilExecutionResult:
        """Execute the full council workflow.
        
        Orchestrates the entire workflow:
        1. Validate request data
        2. Retrieve and validate learning style profile
        3. Build provider-specific prompts
        4. Instantiate providers
        5. Execute providers concurrently
        6. Aggregate results
        
        Args:
            request: The PromptRequest containing all required parameters
            
        Returns:
            CouncilExecutionResult containing responses, provider status, and metrics
            
        Raises:
            CouncilExecutionError: If all providers fail or critical error occurs
        """
        start_time = time.time()
        logger.info("Starting council execution for topic: %s", request.topic)

        try:
            # Step 1: Validate request
            self._validate_request(request)
            
            # Step 2: Validate learning style
            self._validate_learning_style(request.learning_style)

            logger.info(
                "Request validated - Topic: %s, Style: %s",
                request.topic,
                request.learning_style
            )

            # Step 3: Build provider-specific prompts (validates templates exist)
            providers_info = [
                ("groq", "Groq"),
                ("claude", "Claude"),
                ("gemini", "Gemini"),
                ("deepseek", "DeepSeek"),
                ("openrouter", "OpenRouter"),
                ("cerebras", "Cerebras"),
                ("sambanova", "SambaNova"),
            ]
            
            for provider_key, _ in providers_info:
                try:
                    _ = self.build_provider_prompt(
                        provider_name=provider_key,
                        topic=request.topic,
                        objective=request.objective,
                        learning_style=request.learning_style,
                        difficulty=request.difficulty,
                        education_level=request.education_level,
                        output_length=request.output_length,
                    )
                except CouncilExecutionError as e:
                    logger.error("Failed to build prompt for %s: %s", provider_key, str(e))
                    raise

            logger.info("All provider prompts built successfully")

            # Step 4: Instantiate providers
            provider_configs = {
                "Groq": ProviderConfig(
                    provider_name="Groq",
                    role="creator",
                    model_name="llama-3.3-70b-versatile",
                    enabled=True,
                ),
                "Claude": ProviderConfig(
                    provider_name="Claude",
                    role="validator",
                    model_name="claude-3-5-sonnet",
                    enabled=True,
                ),
                "Gemini": ProviderConfig(
                    provider_name="Gemini",
                    role="refiner",
                    model_name="gemini-1.5-pro",
                    enabled=True,
                ),
                "DeepSeek": ProviderConfig(
                    provider_name="DeepSeek",
                    role="critic",
                    model_name="deepseek-chat",
                    enabled=True,
                ),
                "OpenRouter": ProviderConfig(
                    provider_name="OpenRouter",
                    role="creator",
                    model_name="openai/gpt-oss-120b",
                    enabled=True,
                ),
                "Cerebras": ProviderConfig(
                    provider_name="Cerebras",
                    role="creator",
                    model_name="llama-4-scout-17b-16e-instruct",
                    enabled=True,
                ),
                "SambaNova": ProviderConfig(
                    provider_name="SambaNova",
                    role="creator",
                    model_name="Meta-Llama-3.3-70B-Instruct",
                    enabled=True,
                ),
            }

            providers = {
                "Groq": GroqClient(provider_configs["Groq"]),
                "Claude": ClaudeClient(provider_configs["Claude"]),
                "Gemini": GeminiClient(provider_configs["Gemini"]),
                "DeepSeek": DeepSeekClient(provider_configs["DeepSeek"]),
                "OpenRouter": OpenRouterClient(provider_configs["OpenRouter"]),
                "Cerebras": CerebrasClient(provider_configs["Cerebras"]),
                "SambaNova": SambaNovaClient(provider_configs["SambaNova"]),
            }

            logger.info("All providers instantiated")

            # Step 5: Execute providers concurrently
            logger.info("Starting concurrent provider execution")

            tasks = []
            provider_names = []
            for provider_name, provider_instance in providers.items():
                task = self.execute_provider(
                    provider=provider_instance,
                    provider_name=provider_name,
                    topic=request.topic,
                    objective=request.objective,
                    learning_style=request.learning_style,
                    difficulty=request.difficulty,
                    education_level=request.education_level,
                    output_length=request.output_length,
                )
                tasks.append(task)
                provider_names.append(provider_name)

            # Execute all tasks concurrently
            provider_responses = await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("Concurrent provider execution completed")

            # Step 6: Process responses and aggregate results
            result = CouncilExecutionResult()

            for provider_name, response in zip(provider_names, provider_responses):
                if isinstance(response, Exception):
                    logger.error(
                        "Provider %s raised exception: %s",
                        provider_name,
                        str(response)
                    )
                    result.failed_providers.append(provider_name)
                    
                    error_type = type(response).__name__
                    status_code = getattr(response, "status_code", None)
                    if status_code is None:
                        error_str = str(response)
                        import re
                        match = re.search(r"Error code:\s*(\d+)", error_str)
                        if match:
                            status_code = match.group(1)
                        else:
                            status_code = "N/A"
                    
                    result.error_details[provider_name] = {
                        "type": error_type,
                        "status_code": status_code,
                        "message": str(response)
                    }
                elif response is None:
                    logger.warning("Provider %s returned None", provider_name)
                    result.failed_providers.append(provider_name)
                    result.error_details[provider_name] = {
                        "type": "NoneTypeError",
                        "status_code": "N/A",
                        "message": "Provider returned None"
                    }
                else:
                    try:
                        if isinstance(response, dict):
                            # Pass raw output into ResponseNormalizer
                            normalized = self.response_normalizer.normalize(
                                provider_name=provider_name,
                                raw_response=response,
                                role=providers[provider_name].get_role(),
                            )
                        elif isinstance(response, CouncilResponse):
                            # Already normalized CouncilResponse
                            normalized = response
                            if not getattr(normalized, "provider_name", None):
                                normalized.provider_name = provider_name
                        else:
                            raise ValueError(f"Unexpected response type: {type(response)}")

                        result.responses.append(normalized)
                        result.successful_providers.append(provider_name)
                        logger.info("Response collected from provider: %s", provider_name)
                    except Exception as ne:
                        logger.error(
                            "Failed to normalize response for provider %s: %s",
                            provider_name,
                            str(ne),
                        )
                        result.failed_providers.append(provider_name)
                        result.error_details[provider_name] = {
                            "type": "NormalizationError",
                            "status_code": "N/A",
                            "message": f"Normalization failed: {str(ne)}"
                        }

            # Check if at least one provider succeeded
            if not result.responses:
                error_msg = f"All providers failed. Error details: {result.error_details}"
                logger.error(error_msg)
                raise CouncilExecutionError(error_msg)

            # Calculate execution time
            result.execution_time = time.time() - start_time

            logger.info(
                "Council execution completed successfully. "
                "Successful: %s, Failed: %s, Time: %.2fs",
                len(result.successful_providers),
                len(result.failed_providers),
                result.execution_time
            )

            return result

        except CouncilExecutionError:
            raise
        except Exception as e:
            logger.error(
                "CouncilExecutor.execute() failed with unexpected error: %s",
                str(e),
                exc_info=True
            )
            raise CouncilExecutionError(f"Unexpected execution error: {str(e)}")

    async def execute_council(
        self,
        request: PromptRequest,
        timeout: float = 300.0,
    ) -> List[CouncilResponse]:
        """Execute the live council by invoking all active providers in parallel.
        
        Uses asyncio.gather(..., return_exceptions=True) for concurrent execution.
        Succeeds as long as at least one active provider succeeds (failover).
        Updates provider health metrics.
        
        Args:
            request: The PromptRequest containing all required parameters.
            
        Returns:
            List[CouncilResponse]: List of normalized responses from successful providers.
            
        Raises:
            CouncilExecutionError: If all providers fail or a critical error occurs.
        """
        logger.info("Starting execute_council for topic: %s", request.topic)
        self._validate_request(request)
        
        # Build Task Profile and Prompt from intent
        task_type = getattr(request, "task_type", "learning") or "learning"
        intent_val = getattr(request, "intent", "learn") or "learn"
        profile = TaskProfileRegistry.get_profile(task_type)
        
        image_data = getattr(request, "image_data", None)
        input_type = "image" if image_data else "text"
        
        univ_input = UniversalInput(
            raw_content=request.topic, 
            input_type=input_type,
            image_data=image_data
        )
        
        # safely extract subject/domain if they exist in request, or use defaults
        subject_val = getattr(request, "subject", "unknown") or "unknown"
        domain_val = getattr(request, "domain", "unknown") or "unknown"
        intent = DetectedIntent(
            intent=intent_val, 
            task_type=task_type,
            subject=subject_val,
            domain=domain_val
        )
        
        generated_prompt = None
        if task_type != "learning":
            generated_prompt = profile.build_prompt(univ_input, intent)
            style_guidance = ""
        else:
            self._validate_learning_style(request.learning_style)
            # Get full profile for injection
            try:
                style_prof = self.learning_style_engine.get_style_profile(request.learning_style)
                style_guidance = (
                    f"{style_prof.style.upper()} LEARNING STYLE\n"
                    f"Teaching Methods: {', '.join(style_prof.teaching_methods)}\n"
                    f"Content Focus: {', '.join(style_prof.content_focus)}\n"
                    f"Output Preferences: {', '.join(style_prof.output_preferences)}\n"
                    f"Avoid: {', '.join(style_prof.avoid)}"
                )
            except InvalidLearningStyleError:
                style_guidance = request.learning_style

        # Add vision capability filtering if needed
        require_vision = (univ_input.input_type == "image" or getattr(request, "image_data", None) is not None)
        
        if require_vision:
            active_providers = self.provider_registry.get_providers_with_capability("vision")
            if not active_providers:
                raise CouncilExecutionError("No active vision-capable providers found in the registry.")
        else:
            active_providers = self.provider_registry.get_active_providers()
            if not active_providers:
                raise CouncilExecutionError("No active providers found in the registry.")

        tasks = []
        provider_names = list(active_providers.keys())

        for name, provider_instance in active_providers.items():
            suitability = profile.get_provider_suitability(provider_instance.get_provider_name())
            coro = self.execute_provider(
                provider=provider_instance,
                provider_name=provider_instance.get_provider_name(),
                topic=request.topic,
                objective=request.objective,
                learning_style=style_guidance,
                difficulty=request.difficulty,
                education_level=request.education_level,
                bloom_level=request.bloom_level,
                output_length=request.output_length,
                timeout=timeout,
                prompt=generated_prompt,
                suitability_score=suitability,
            )
            task = asyncio.create_task(coro)
            tasks.append(task)

        # Generate request ID if missing
        import uuid
        req_id = getattr(request, "id", None) or str(uuid.uuid4())[:8]

        # Execute simultaneously using wait with strict timeout
        logger.info("[Req:%s] Gathering %d provider tasks with %.1fs strict timeout", req_id, len(tasks), timeout)
        done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.ALL_COMPLETED)
        
        # Cancel any pending tasks that took longer than timeout
        for p_task in pending:
            p_task.cancel()
            
        results = []
        for task in tasks:
            if task in done:
                try:
                    results.append(task.result())
                except Exception as e:
                    results.append(e)
            else:
                results.append(TimeoutError(f"Provider timed out after {timeout} seconds"))

        normalized_responses: List[CouncilResponse] = []
        self.failed_providers = []
        self.successful_providers = []
        self.error_details = {}

        for name, response in zip(provider_names, results):
            provider_instance = active_providers[name]
            provider_display_name = provider_instance.get_provider_name()

            if isinstance(response, Exception):
                logger.error("[Req:%s] Provider %s execution failed: %s", req_id, provider_display_name, response, exc_info=response)
                self.failed_providers.append(provider_display_name)
                
                error_type = type(response).__name__
                status_code = getattr(response, "status_code", None)
                if status_code is None:
                    error_str = str(response)
                    import re
                    match = re.search(r"Error code:\s*(\d+)", error_str)
                    if match:
                        status_code = match.group(1)
                    else:
                        status_code = "N/A"
                        
                self.error_details[provider_display_name] = {
                    "type": error_type,
                    "status_code": status_code,
                    "message": str(response) if str(response) else error_type
                }
                
                is_timeout = "timeout" in error_type.lower() or "timeout" in str(response).lower()
                self.health_tracker.record_failure(provider_display_name, is_timeout=is_timeout)
            elif response is None:
                logger.warning("[Req:%s] Provider %s returned None", req_id, provider_display_name)
                self.failed_providers.append(provider_display_name)
                self.error_details[provider_display_name] = {
                    "type": "NoneTypeError",
                    "status_code": "N/A",
                    "message": "Provider returned None"
                }
                self.health_tracker.record_failure(provider_display_name, is_timeout=False)
            else:
                try:
                    logger.info(f"Before response normalization for {provider_display_name}")
                    if isinstance(response, dict):
                        # Normalize raw dict response
                        normalized = self.response_normalizer.normalize(
                            provider_name=provider_display_name,
                            raw_response=response,
                            role=provider_instance.get_role(),
                        )
                    elif isinstance(response, CouncilResponse):
                        normalized = response
                        if not getattr(normalized, "provider_name", None):
                            normalized.provider_name = provider_display_name
                    else:
                        raise ValueError(f"Unexpected response type: {type(response)}")
                        
                    # Ensure suitability_score is passed along if normalized from dict
                    if isinstance(response, dict):
                        suitability = profile.get_provider_suitability(provider_display_name)
                        if getattr(normalized, "metadata", None) is None:
                            from src.models.council_response import ResponseMetadata
                            normalized.metadata = ResponseMetadata()
                        normalized.metadata.suitability_score = suitability
                    logger.info(f"After response normalization for {provider_display_name}")

                    normalized_responses.append(normalized)
                    self.successful_providers.append(provider_display_name)
                    
                    # Record health metrics
                    res_time = normalized.metadata.response_time if (normalized.metadata and normalized.metadata.response_time) else 0.0
                    self.health_tracker.record_success(provider_display_name, response_time=res_time)
                    logger.info("[Req:%s] Successfully normalized response for %s (Latency: %.2fs)", req_id, provider_display_name, res_time)
                except Exception as ne:
                    logger.error("[Req:%s] Failed to normalize response for %s: %s", req_id, provider_display_name, ne)
                    self.failed_providers.append(provider_display_name)
                    self.error_details[provider_display_name] = {
                        "type": "NormalizationError",
                        "status_code": "N/A",
                        "message": f"Normalization failed: {str(ne)}"
                    }
                    self.health_tracker.record_failure(provider_display_name, is_timeout=False)

        if not normalized_responses:
            error_msg = f"[Req:{req_id}] All providers failed. Error details: {self.error_details}"
            logger.error(error_msg)
            raise CouncilExecutionError(error_msg, error_details=self.error_details)

        logger.info(
            "[Req:%s] execute_council completed. Successful: %s, Failed: %s",
            req_id,
            len(self.successful_providers),
            len(self.failed_providers)
        )
        return normalized_responses
