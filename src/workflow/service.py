from typing import Any, Dict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.prompts import crud as prompts_crud
from src.council_responses import crud as council_crud
from src.consensus_results import crud as consensus_crud
from src.explanations import crud as explanations_crud


def run_workflow(db: Session, request_id: int, user_id: int) -> Dict[str, Any]:
    """Load related models for a PromptRequest and return a combined result.

    Raises HTTPException(404) if the PromptRequest does not exist or is not owned by the user.
    """

    request = prompts_crud.get_prompt_request(db=db, request_id=request_id)

    if request is None or int(request.user_id) != int(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    # Load council responses
    council_responses = council_crud.get_council_responses_by_request(db=db, request_id=request_id)

    # Load consensus result (may be None)
    consensus_result = consensus_crud.get_consensus_result(db=db, request_id=request_id)

    # Load explanation (may be None)
    explanation = explanations_crud.get_explanation_by_request(db=db, request_id=request_id)

    return {
        "request_id": int(request.id),
        "prompt_request": request,
        "council_responses": council_responses,
        "consensus_result": consensus_result,
        "explanation": explanation,
    }
