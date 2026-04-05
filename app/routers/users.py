from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.core.exceptions import ForbiddenError
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Any authenticated user can view their own profile."""
    return current_user


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin only: list all users in the system."""
    return user_service.get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admins can view any user's profile.
    Non-admins can only view their own.
    """
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise ForbiddenError("You can only view your own profile")
    return user_service.get_user_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admin only: update a user's role, email, or active status."""
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Admin only: permanently delete a user.
    Admins cannot delete their own account (prevents accidental lockout).
    """
    if current_user.id == user_id:
        raise ForbiddenError("You cannot delete your own account")
    user_service.delete_user(db, user_id)
