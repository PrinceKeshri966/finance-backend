from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User, UserRole

# This tells FastAPI to look for "Authorization: Bearer <token>"
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Core auth dependency. Decodes the JWT, loads the user from DB,
    and returns them. Raises 401 for anything invalid.
    """
    payload = decode_access_token(credentials.credentials)

    if not payload:
        raise UnauthorizedError("Token is invalid or has expired")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token is malformed — missing subject")

    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active == True
    ).first()

    if not user:
        raise UnauthorizedError("User account does not exist or has been deactivated")

    return user


def require_roles(*roles: UserRole):
    """
    A dependency factory. Returns a dependency that only allows through
    users whose role is in the provided list.

    Usage:
        Depends(require_roles(UserRole.ADMIN))
        Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))
    """
    def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise ForbiddenError(
                f"Access denied. This action requires one of these roles: {allowed}"
            )
        return current_user

    return check_role


# Shorthand dependencies — import these directly in routers
require_admin = require_roles(UserRole.ADMIN)
require_analyst_or_above = require_roles(UserRole.ANALYST, UserRole.ADMIN)
require_any_authenticated = require_roles(UserRole.VIEWER, UserRole.ANALYST, UserRole.ADMIN)
