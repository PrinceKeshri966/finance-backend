from datetime import date
from typing import Any, Dict, List

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType


def get_summary(db: Session) -> Dict[str, Any]:
    """
    The headline numbers at the top of any finance dashboard.
    Using scalar() so we get a float directly, and `or 0.0` handles
    the edge case where there are no transactions yet.
    """
    base = db.query(Transaction).filter(Transaction.is_deleted == False)

    total_income = (
        base.filter(Transaction.type == TransactionType.INCOME)
        .with_entities(func.sum(Transaction.amount))
        .scalar() or 0.0
    )

    total_expense = (
        base.filter(Transaction.type == TransactionType.EXPENSE)
        .with_entities(func.sum(Transaction.amount))
        .scalar() or 0.0
    )

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expense, 2),
        "net_balance": round(total_income - total_expense, 2),
        "total_transactions": base.count(),
    }


def get_category_breakdown(db: Session) -> Dict[str, Any]:
    """
    Per-category totals split by income and expense.
    Useful for pie/donut charts on the dashboard.
    """
    rows = (
        db.query(
            Transaction.category,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.is_deleted == False)
        .group_by(Transaction.category, Transaction.type)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    breakdown: Dict[str, Any] = {}
    for row in rows:
        if row.category not in breakdown:
            breakdown[row.category] = {}
        breakdown[row.category][row.type.value] = {
            "total": round(row.total, 2),
            "count": row.count,
        }

    return breakdown


def get_monthly_trends(db: Session, year: int = None) -> List[Dict]:
    """
    Monthly income vs expense for the requested year.

    We always return all 12 months (with zeroes for months with no data).
    This way the frontend can render a complete bar chart without gaps.
    """
    if not year:
        year = date.today().year

    rows = (
        db.query(
            extract("month", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.is_deleted == False,
            extract("year", Transaction.date) == year,
        )
        .group_by("month", Transaction.type)
        .order_by("month")
        .all()
    )

    # Pre-fill all 12 months with zeros — prevents frontend from dealing with gaps
    months = {
        i: {"month": i, "income": 0.0, "expense": 0.0}
        for i in range(1, 13)
    }

    for row in rows:
        m = int(row.month)
        key = "income" if row.type == TransactionType.INCOME else "expense"
        months[m][key] = round(row.total, 2)

    return list(months.values())


def get_recent_activity(db: Session, limit: int = 10) -> List[Transaction]:
    """Most recent transactions — for an activity feed or notification panel."""
    return (
        db.query(Transaction)
        .filter(Transaction.is_deleted == False)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )
