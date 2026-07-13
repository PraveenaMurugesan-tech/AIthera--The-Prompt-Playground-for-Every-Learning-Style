from typing import Annotated, List
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.prompts import crud as prompts_crud
from src.council_responses import crud, schemas


router = APIRouter(prefix="/council-responses", tags=["council-responses"])


@router.post("/", response_model=schemas.CouncilResponseOut, status_code=status.HTTP_201_CREATED)
def create_council_response(
    payload: schemas.CouncilResponseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.CouncilResponseOut:
    """Create a CouncilResponse for a PromptRequest owned by the user."""

    owner_id = prompts_crud.get_prompt_request_owner(db=db, request_id=payload.request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    response = crud.create_council_response(
        db=db,
        request_id=payload.request_id,
        model=payload.model,
        role=payload.role,
        prompt=payload.prompt,
        reasoning=payload.reasoning,
        strengths=payload.strengths,
        metadata=payload.metadata,
    )

    # Convert strengths from stored JSON string to list if needed
    strengths_out = []
    try:
        if response.strengths:
            strengths_out = json.loads(response.strengths)
    except Exception:
        strengths_out = [s for s in (response.strengths or "").splitlines() if s]

    return schemas.CouncilResponseOut(
        id=int(response.id),
        request_id=int(response.request_id),
        model=response.model,
        role=response.role,
        prompt=response.prompt,
        reasoning=response.reasoning,
        strengths=strengths_out,
        metadata=response.response_metadata,
        created_at=response.created_at,
    )


@router.get("/{request_id}", response_model=List[schemas.CouncilResponseOut])
def get_council_responses(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[schemas.CouncilResponseOut]:
    """Return all CouncilResponses for a PromptRequest owned by the user."""

    owner_id = prompts_crud.get_prompt_request_owner(db=db, request_id=request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    responses = crud.get_council_responses_by_request(db=db, request_id=request_id)

    out = []
    for r in responses:
        strengths_out = []
        try:
            if r.strengths:
                strengths_out = json.loads(r.strengths)
        except Exception:
            strengths_out = [s for s in (r.strengths or "").splitlines() if s]

        out.append(
            schemas.CouncilResponseOut(
                id=int(r.id),
                request_id=int(r.request_id),
                model=r.model,
                role=r.role,
                prompt=r.prompt,
                reasoning=r.reasoning,
                strengths=strengths_out,
                metadata=r.response_metadata,
                created_at=r.created_at,
            )
        )

    return out
