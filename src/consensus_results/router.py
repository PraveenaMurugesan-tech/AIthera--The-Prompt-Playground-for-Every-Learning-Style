from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.prompts import crud as prompts_crud
from src.consensus_results import crud, schemas


router = APIRouter(prefix="/consensus-results", tags=["consensus-results"])


@router.post("/", response_model=schemas.ConsensusResultOut, status_code=status.HTTP_201_CREATED)
def create_consensus_result(
    payload: schemas.ConsensusResultCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.ConsensusResultOut:
    """Create or return the ConsensusResult for a PromptRequest owned by the user."""

    owner_id = prompts_crud.get_prompt_request_owner(db=db, request_id=payload.request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    result = crud.create_consensus_result(
        db=db,
        request_id=payload.request_id,
        final_prompt=payload.final_prompt,
        quality_score=payload.quality_score,
        consensus_reasoning=payload.consensus_reasoning,
        combined_strengths=payload.combined_strengths,
        contributors=payload.contributors,
        response_count=payload.response_count,
        metadata=payload.metadata,
    )

    return schemas.ConsensusResultOut(
        id=int(result.id),
        request_id=int(result.request_id),
        final_prompt=result.final_prompt,
        quality_score=result.quality_score,
        consensus_reasoning=result.consensus_reasoning,
        combined_strengths=result.combined_strengths,
        contributors=result.contributors,
        response_count=result.response_count,
        response_metadata=result.response_metadata,
        created_at=result.created_at,
    )


@router.get("/{request_id}", response_model=schemas.ConsensusResultOut)
def get_consensus_result(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.ConsensusResultOut:
    """Return the ConsensusResult for a PromptRequest owned by the user."""

    owner_id = prompts_crud.get_prompt_request_owner(db=db, request_id=request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    result = crud.get_consensus_result(db=db, request_id=request_id)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ConsensusResult not found")

    return schemas.ConsensusResultOut(
        id=int(result.id),
        request_id=int(result.request_id),
        final_prompt=result.final_prompt,
        quality_score=result.quality_score,
        consensus_reasoning=result.consensus_reasoning,
        combined_strengths=result.combined_strengths,
        contributors=result.contributors,
        response_count=result.response_count,
        response_metadata=result.response_metadata,
        created_at=result.created_at,
    )
