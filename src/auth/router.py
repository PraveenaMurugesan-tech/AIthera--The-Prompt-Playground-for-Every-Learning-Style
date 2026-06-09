from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.models.user import User

from . import crud, schemas, security

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Return the currently authenticated user from the JWT token.
    """

    try:
        payload = security.decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post(
    "/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: schemas.UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> schemas.UserOut:
    """
    Register a new user.
    """

    existing_user = crud.get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = crud.create_user(
        db,
        email=payload.email,
        password=payload.password,
    )

    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.Token:
    """
    Authenticate a user and return a JWT access token.
    """

    user = crud.authenticate_user(
        db,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = security.create_access_token(
        subject=str(user.id)
    )

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me", response_model=schemas.UserOut)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> schemas.UserOut:
    """
    Return information about the authenticated user.
    """

    return current_user