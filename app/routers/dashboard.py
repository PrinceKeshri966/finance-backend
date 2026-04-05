from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Top-level numbers: total income, total expenses, net balance,
    and transaction count. All roles can access this.
    """
    return dashboard_service.get_summary(db)


@router.get("/categories")
def get_category_breakdown(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Per-category totals broken down by income and expense.
    Good for pie charts or ranked category lists.
    """
    return dashboard_service.get_category_breakdown(db)


@router.get("/trends")
def get_monthly_trends(
    year: int = Query(None, description="Year to pull trends for. Defaults to current year."),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Month-by-month income vs expense for the given year.
    Always returns all 12 months (zero-filled) so the frontend
    can render a complete chart without handling missing months.
    """
    return dashboard_service.get_monthly_trends(db, year)


@router.get("/recent", response_model=List[TransactionResponse])
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="How many recent transactions to return"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Most recent transactions — for an activity feed widget."""
    records = dashboard_service.get_recent_activity(db, limit)
    return [TransactionResponse.model_validate(r) for r in records]
