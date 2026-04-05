from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    require_admin,
    require_analyst_or_above,
)
from app.database import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.transaction import (
    PaginatedTransactions,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.services import transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_above),
):
    """Analyst and Admin can create transactions. Viewers cannot."""
    return transaction_service.create_transaction(db, data, current_user)


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    type: Optional[TransactionType] = Query(None, description="Filter by income or expense"),
    category: Optional[str] = Query(None, description="Partial match on category name"),
    date_from: Optional[date] = Query(None, description="Start of date range (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End of date range (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
):
    """
    All roles can list transactions.
    Supports filtering by type, category, and date range, plus pagination.
    """
    records, total = transaction_service.get_transactions(
        db,
        tx_type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )

    return PaginatedTransactions(
        data=[TransactionResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{tx_id}", response_model=TransactionResponse)
def get_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """All roles can view a single transaction."""
    return transaction_service.get_transaction_by_id(db, tx_id)


@router.patch("/{tx_id}", response_model=TransactionResponse)
def update_transaction(
    tx_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_above),
):
    """Analyst and Admin can update transactions."""
    return transaction_service.update_transaction(db, tx_id, data)


@router.delete("/{tx_id}", status_code=204)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """
    Admin only: soft-deletes a transaction.
    The record remains in the DB but is hidden from all queries.
    """
    transaction_service.soft_delete_transaction(db, tx_id)
