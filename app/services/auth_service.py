from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def register_user(db: Session, data: UserCreate) -> User:
    """
    Creates a new user. We check both username and email uniqueness
    before inserting to give clear, field-specific error messages.
    """
    if db.query(User).filter(User.username == data.username).first():
        raise ConflictError(f"The username '{data.username}' is already taken")

    if db.query(User).filter(User.email == data.email).first():
        raise ConflictError(f"The email '{data.email}' is already registered")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, username: str, password: str) -> str:
    """
    Validates credentials and returns a signed JWT.

    We deliberately use the same error message for wrong username AND wrong password.
    This is intentional — telling an attacker which one is wrong gives away information.
    """
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect username or password")

    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated. Contact an admin.")

    # Embed role in token so role checks don't always need a DB hit
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return token
