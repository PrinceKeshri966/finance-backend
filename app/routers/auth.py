from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Role defaults to `viewer` unless explicitly set.
    In a real product you'd probably lock this to admin-only for non-viewer roles.
    """
    return auth_service.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Returns a JWT Bearer token.
    Include this in subsequent requests as: `Authorization: Bearer <token>`
    """
    token = auth_service.login_user(db, data.username, data.password)
    return {"access_token": token}
