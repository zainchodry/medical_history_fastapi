import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── Enums ────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    doctor = "doctor"
    patient = "patient"
    admin = "admin"


# ── Base / Create ────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    role: UserRole = UserRole.patient


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = None


# ── Login ────────────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ── Response ─────────────────────────────────────────────────
class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str | None = None
    is_active: int = 1
    created_at: datetime | None = None


# ── Token ────────────────────────────────────────────────────
class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Password flows ──────────────────────────────────────────
class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    password: str = Field(min_length=6, max_length=128)


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)
    confirm_password: str
