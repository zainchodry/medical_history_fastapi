from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.user import (
    ChangePasswordSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    TokenSchema,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)
from app.utils.auth import create_access_token
from app.utils.deps import CurrentUserDep
from app.utils.email import send_reset_email
from app.utils.password import hash_password, verify_password
from app.utils.token import generate_reset_token, verify_reset_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Register ─────────────────────────────────────────────────
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        username=data.username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # audit
    db.add(AuditLog(user_id=user.id, action="CREATE", resource="user", resource_id=user.id))
    db.commit()

    return user


# ── Login ────────────────────────────────────────────────────
@router.post("/login", response_model=TokenSchema)
def login(
    data: UserLogin,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact an administrator.",
        )

    token = create_access_token({"user_id": user.id, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


# ── Me (profile) ─────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
def get_me(current_user: CurrentUserDep):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
):
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


# ── Change Password (authenticated) ─────────────────────────
@router.post("/change-password")
def change_password(
    data: ChangePasswordSchema,
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
):
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match",
        )

    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ── Forgot Password ─────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordSchema,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        # return success even if user not found (prevent email enumeration)
        return {"message": "If this email exists, a reset link has been sent"}

    token = generate_reset_token(user.email)
    link = f"{settings.FRONTEND_URL}/reset-password/{token}"
    await send_reset_email(user.email, link)

    return {"message": "If this email exists, a reset link has been sent"}


# ── Reset Password ──────────────────────────────────────────
@router.post("/reset-password/{token}")
def reset_password(
    token: str,
    data: ResetPasswordSchema,
    db: Annotated[Session, Depends(get_db)],
):
    email = verify_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password = hash_password(data.password)
    db.commit()
    return {"message": "Password reset successful"}


# ── List Users (admin only) ─────────────────────────────────
@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: CurrentUserDep,
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return db.query(User).offset(skip).limit(limit).all()