from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.auth.router import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.prompts import crud, schemas


router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=schemas.PromptRequestResponse, status_code=status.HTTP_201_CREATED)
def create_prompt(
    payload: schemas.PromptRequestCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.PromptRequestResponse:
    """
    Create a new PromptRequest for the authenticated user.

    Returns the created PromptRequest with a 201 status code.
    """

    request = crud.create_prompt_request(
        db,
        user_id=int(current_user.id),
        topic=payload.topic,
        learning_style=payload.learning_style,
        difficulty=payload.difficulty,
    )

    return request


@router.get("/", response_model=List[schemas.PromptRequestResponse])
def list_prompts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[schemas.PromptRequestResponse]:
    """
    Return all PromptRequests for the authenticated user, newest first.
    """

    results = crud.get_user_prompt_requests(db, user_id=int(current_user.id))
    return results


@router.get("/{request_id}", response_model=schemas.PromptRequestResponse)
def get_prompt(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.PromptRequestResponse:
    """
    Return a single PromptRequest by id for the authenticated user.

    Returns 404 if the PromptRequest does not exist or does not belong to the user.
    """

    request = crud.get_prompt_request(db, request_id=request_id)

    if request is None or int(request.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """
    Delete a PromptRequest owned by the authenticated user.

    Returns 204 No Content on success, or 404 if not found / not owned.
    """

    request = crud.get_prompt_request(db, request_id=request_id)

    if request is None or int(request.user_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PromptRequest not found")

    deleted = crud.delete_prompt_request(db, request_id=request_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete prompt request")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
