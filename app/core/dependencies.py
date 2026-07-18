from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token

# This tells FastAPI: "expect a token in the Authorization header,
# as 'Bearer <token>'". tokenUrl just points Swagger's /docs UI to
# our login endpoint so it knows where to get a token from — it
# doesn't affect how this dependency actually works.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Runs on every route that needs "must be logged in".
    FastAPI extracts the token from the request header automatically
    (via oauth2_scheme above), then we verify it and load the actual
    User row it refers to.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_error

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_error

    return user


def require_role(*allowed_roles: UserRole):
    """
    A 'dependency factory' — a function that RETURNS a dependency,
    customized by argument. This lets us write:
        Depends(require_role(UserRole.DOCTOR))
    instead of writing a separate near-identical function for every
    role combination we need to guard.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: "
                       f"{[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker
