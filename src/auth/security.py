import os
from datetime import datetime, timedelta
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Read JWT settings from environment with safe defaults for development.
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "please-change-this-secret"))
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def get_password_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt."""

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: int | None = None) -> str:
    """Create a JWT access token with a subject (typically user id).

    The token contains `sub` and `exp` claims.
    """

    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: Dict[str, Any] = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token, raising JWTError on failure."""

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])