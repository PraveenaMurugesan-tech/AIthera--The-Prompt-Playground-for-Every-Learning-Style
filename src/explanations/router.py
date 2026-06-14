from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.prompts import crud as prompts_crud
from src.explanations import crud, schemas


router = APIRouter(prefix="/explanations", tags=["explanations"])


@router.post("/{request_id}/generate", response_model=schemas.ExplanationOut, status_code=status.HTTP_201_CREATED)
def generate_explanation(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.ExplanationOut:
    """Generate and persist an Explanation for a PromptRequest owned by the user."""

    request = prompts_crud.get_prompt_request(db=db, request_id=request_id)

    if request is None or int(request.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    topic = request.topic
    learning_style = request.learning_style
    difficulty = request.difficulty

    content = (
        f"This explanation was generated for the topic '{topic}' "
        f"using the '{learning_style}' learning style at '{difficulty}' difficulty."
    )

    explanation = crud.create_explanation(db=db, request_id=request_id, content=content)

    return schemas.ExplanationOut(
        id=int(explanation.id),
        request_id=int(explanation.request_id),
        content=explanation.explanation,
        created_at=explanation.created_at,
    )


@router.get("/{request_id}", response_model=schemas.ExplanationOut)
def get_explanation(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.ExplanationOut:
    """Return the Explanation for a PromptRequest if it exists and is owned by the user."""

    request = prompts_crud.get_prompt_request(db=db, request_id=request_id)

    if request is None or int(request.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    explanation = crud.get_explanation_by_request(db=db, request_id=request_id)

    if explanation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found")

    return schemas.ExplanationOut(
        id=int(explanation.id),
        request_id=int(explanation.request_id),
        content=explanation.explanation,
        created_at=explanation.created_at,
    )


@router.delete("/{request_id}")
def delete_explanation(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Delete the Explanation associated with a PromptRequest owned by the user."""

    # Ownership check
    owner_id = prompts_crud.get_prompt_request_owner(db=db, request_id=request_id)

    if owner_id is None or int(owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    explanation = crud.get_explanation_by_request(db=db, request_id=request_id)

    if explanation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found")

    deleted = crud.delete_explanation(db=db, explanation=explanation)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete explanation")

    return {"message": "Explanation deleted successfully"}
