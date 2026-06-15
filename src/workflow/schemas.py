from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from src.prompts.schemas import PromptRequestResponse
from src.council_responses.schemas import CouncilResponseOut
from src.consensus_results.schemas import ConsensusResultOut
from src.explanations.schemas import ExplanationOut


class WorkflowResponse(BaseModel):
    request_id: int
    prompt_request: PromptRequestResponse
    council_responses: List[CouncilResponseOut]
    consensus_result: Optional[ConsensusResultOut] = None
    explanation: Optional[ExplanationOut] = None

    model_config = ConfigDict(from_attributes=True)
