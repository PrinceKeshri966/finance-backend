import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum,
    Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(SAEnum(TransactionType), nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    notes = Column(Text, nullable=True)

    # Soft delete: we mark records as deleted instead of removing them.
    # This preserves history and makes accidental-delete recovery possible.
    is_deleted = Column(Boolean, default=False, nullable=False)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    creator = relationship(
        "User",
        back_populates="transactions",
        foreign_keys=[created_by_id]
    )

    def __repr__(self):
        return f"<Transaction {self.type} ₹{self.amount} [{self.category}]>"
