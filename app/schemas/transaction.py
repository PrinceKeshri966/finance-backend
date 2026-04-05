from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.models.transaction import TransactionType
from app.schemas.user import UserSummary


class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def clean_category(cls, v: str) -> str:
        # Title-case so "food", "Food", "FOOD" all store as "Food"
        return v.strip().title()


class TransactionUpdate(BaseModel):
    """Partial update — send only what changed."""
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def clean_category(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().title() if v else v


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    creator: UserSummary
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTransactions(BaseModel):
    data: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
