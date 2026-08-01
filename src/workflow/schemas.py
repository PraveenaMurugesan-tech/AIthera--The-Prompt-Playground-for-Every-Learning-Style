from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

from src.prompts.schemas import PromptRequestResponse
from src.council_responses.schemas import CouncilResponseOut
from src.consensus_results.schemas import ConsensusResultOut
from src.explanations.schemas import ExplanationOut


class UniversalInput(BaseModel):
    input_type: Literal["text", "voice", "image"]
    raw_content: Optional[str] = None
    transcript: Optional[str] = None
    image_data: Optional[str] = None # Base64 encoded or reference
    mime_type: Optional[str] = None
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectedIntent(BaseModel):
    intent: str
    domain: str
    task_type: str
    subject: str
    style: Optional[str] = None
    output_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    request_id: int
    prompt_request: PromptRequestResponse
    council_responses: List[CouncilResponseOut]
    consensus_result: Optional[ConsensusResultOut] = None
    explanation: Optional[ExplanationOut] = None

    model_config = ConfigDict(from_attributes=True)
