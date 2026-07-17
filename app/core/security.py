from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext handles the actual bcrypt hashing/verifying for us.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Turns a plain password into a one-way bcrypt hash for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks a login attempt's password against the stored hash.
    Returns True/False — we never decrypt the hash, we just compare.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Builds a signed JWT. 'data' typically contains the user's id and role
    (e.g. {"sub": "5", "role": "patient"}) — 'sub' is the JWT-standard
    field name for 'subject', i.e. who this token belongs to.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # jwt.encode signs the token using our SECRET_KEY — this signature
    # is what makes the token unforgeable without that key.
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Verifies a token's signature and expiration.
    Returns the decoded payload if valid, or None if the token is
    fake, tampered with, or expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
