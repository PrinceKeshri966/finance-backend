from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, data: TransactionCreate, creator: User) -> Transaction:
    tx = Transaction(**data.model_dump(), created_by_id=creator.id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transactions(
    db: Session,
    tx_type: Optional[TransactionType] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Transaction], int]:
    """
    Returns a paginated list of non-deleted transactions.
    Tuple is (records, total_count) so callers can compute total pages.
    """
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    if category:
        # Case-insensitive partial match — handy for search-as-you-type
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    total = query.count()
    offset = (page - 1) * page_size
    records = (
        query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return records, total


def get_transaction_by_id(db: Session, tx_id: int) -> Transaction:
    tx = db.query(Transaction).filter(
        Transaction.id == tx_id,
        Transaction.is_deleted == False,
    ).first()
    if not tx:
        raise NotFoundError("Transaction", tx_id)
    return tx


def update_transaction(db: Session, tx_id: int, data: TransactionUpdate) -> Transaction:
    tx = get_transaction_by_id(db, tx_id)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)

    db.commit()
    db.refresh(tx)
    return tx


def soft_delete_transaction(db: Session, tx_id: int) -> None:
    """
    Marks the transaction as deleted without removing it from the DB.
    This preserves audit history and makes recovery possible.
    """
    tx = get_transaction_by_id(db, tx_id)
    tx.is_deleted = True
    db.commit()
