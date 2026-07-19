from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.user import UserSignup, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user

# APIRouter lets us group related endpoints together instead of
# cramming everything into main.py. prefix="/auth" means every route
# below automatically starts with /auth (e.g. /auth/signup).
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    """
    Creates a new User row, hashes their password, and creates the
    matching Patient or Doctor profile row based on their chosen role.
    """
    # Admin accounts are never created through this public endpoint —
    # only directly in the database by whoever controls the deployment.
    # Otherwise anyone could sign up and grant themselves admin access.
    if payload.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin accounts cannot be created through signup.",
        )

    # Step 1: reject duplicate emails before doing anything else.
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Step 2: create the core User row (shared by every role).
    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(new_user)
    db.flush()  # sends the INSERT so new_user.id is available, without fully committing yet

    # Step 3: create the role-specific profile row.
    if payload.role == UserRole.PATIENT:
        db.add(Patient(user_id=new_user.id, date_of_birth=payload.date_of_birth))
    elif payload.role == UserRole.DOCTOR:
        db.add(
            Doctor(
                user_id=new_user.id,
                specialization=payload.specialization or "General",
            )
        )
    # ADMIN role has no separate profile table — the User row is enough.

    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Verifies email + password, and if correct, issues a JWT.

    We use OAuth2PasswordRequestForm here (instead of a plain JSON
    body) because it's the standard FastAPI/OAuth2 convention — it's
    what powers the "Authorize" button in /docs, and what most
    frontend OAuth2 tooling expects. Its 'username' field is where
    we receive the email (OAuth2's spec calls it username, but
    nothing stops us from putting an email address in it).
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    # We deliberately give the SAME error message whether the email
    # doesn't exist OR the password is wrong. If we said "email not
    # found" vs "wrong password" separately, an attacker could use
    # that difference to figure out which emails are registered.
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    A protected route: Depends(get_current_user) means FastAPI won't
    even run this function unless a valid token was sent. If the
    token's missing or invalid, the dependency itself raises a 401
    before we ever get here.
    """
    return current_user
