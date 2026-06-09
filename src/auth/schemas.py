from pydantic import BaseModel, EmailStr, Field, constr


class UserCreate(BaseModel):
    """Schema for user registration input."""

    email: EmailStr = Field(..., example="alice@example.com")
    password: constr(min_length=8, max_length=128) = Field(
        ..., example="s3cureP@ssw0rd"
    )


class UserLogin(BaseModel):
    """Schema for user authentication input."""

    email: EmailStr = Field(..., example="alice@example.com")
    password: constr(min_length=8, max_length=128) = Field(
        ..., example="s3cureP@ssw0rd"
    )


class UserOut(BaseModel):
    """Public representation of a user returned by the API."""

    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"