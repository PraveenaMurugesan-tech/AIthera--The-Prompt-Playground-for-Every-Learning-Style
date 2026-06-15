from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.workflow import service, schemas


router = APIRouter(prefix="/workflow", tags=["Workflow"])


@router.post("/{request_id}/run", response_model=schemas.WorkflowResponse)
def run_workflow_endpoint(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.WorkflowResponse:
    """Run the full workflow for a PromptRequest owned by the authenticated user."""

    result = service.run_workflow(db=db, request_id=request_id, user_id=int(current_user.id))

    return schemas.WorkflowResponse(
        request_id=result["request_id"],
        prompt_request=result["prompt_request"],
        council_responses=result["council_responses"],
        consensus_result=result["consensus_result"],
        explanation=result["explanation"],
    )
