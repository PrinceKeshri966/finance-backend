import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    """
    Three-tier access model.
    str mixin makes the enum JSON-serialisable automatically.
    """
    VIEWER = "viewer"      # read-only access
    ANALYST = "analyst"    # read + write transactions
    ADMIN = "admin"        # full access including user management


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    transactions = relationship(
        "Transaction",
        back_populates="creator",
        foreign_keys="Transaction.created_by_id"
    )

    def __repr__(self):
        return f"<User {self.username!r} role={self.role}>"
