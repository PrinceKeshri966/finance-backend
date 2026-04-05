from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.user import UserUpdate


def get_all_users(db: Session) -> List[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User", user_id)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)

    # If email is changing, make sure it isn't already taken by someone else
    if data.email and data.email != user.email:
        if db.query(User).filter(User.email == data.email).first():
            raise ConflictError(f"The email '{data.email}' is already in use")

    # model_dump(exclude_unset=True) only returns fields explicitly sent in the request
    # so we don't accidentally overwrite fields with None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
