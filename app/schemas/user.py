from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserSignup(BaseModel):
    """
    What the client sends us when creating an account.
    Pydantic validates this automatically — e.g. EmailStr rejects
    "not-an-email" before our code even runs, and min_length rejects
    a 3-character password.
    """
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole

    # Optional fields, only relevant depending on role.
    # None = "not provided", which is fine for a doctor signing up
    # (they won't have a date_of_birth field to fill, etc.)
    date_of_birth: date | None = None
    specialization: str | None = None




class UserOut(BaseModel):
    """
    What we send BACK to the client after signup/login or when
    fetching a profile. Notice: no password or password_hash here —
    this is the safety boundary that prevents ever leaking it.
    """
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    # This tells Pydantic "it's fine to build this schema directly
    # from a SQLAlchemy model object, not just a dict."
    class Config:
        from_attributes = True


class Token(BaseModel):
    """What we return after a successful login."""
    access_token: str
    token_type: str = "bearer"
