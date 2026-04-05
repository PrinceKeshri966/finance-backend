"""
Seed script — populates the database with demo users and transactions.

Run once before testing:
    python seed.py

Demo accounts created:
    admin   / admin123   → full access
    analyst / analyst123 → can read and write transactions
    viewer  / viewer123  → read-only
"""

import random
from datetime import date, timedelta

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Wipe existing seed data for a clean run
db.query(Transaction).delete()
db.query(User).delete()
db.commit()

# ── Users ────────────────────────────────────────────────────────────────────

admin = User(
    username="admin",
    email="admin@finance.local",
    hashed_password=hash_password("admin123"),
    role=UserRole.ADMIN,
)
analyst = User(
    username="analyst",
    email="analyst@finance.local",
    hashed_password=hash_password("analyst123"),
    role=UserRole.ANALYST,
)
viewer = User(
    username="viewer",
    email="viewer@finance.local",
    hashed_password=hash_password("viewer123"),
    role=UserRole.VIEWER,
)

db.add_all([admin, analyst, viewer])
db.commit()
db.refresh(admin)

# ── Transactions ──────────────────────────────────────────────────────────────

income_categories = ["Salary", "Freelance", "Investment", "Rental Income", "Bonus"]
expense_categories = ["Food", "Transport", "Utilities", "Healthcare", "Shopping", "Rent", "Entertainment", "Subscriptions"]

transactions = []
today = date.today()

for i in range(80):
    tx_type = random.choices(
        [TransactionType.INCOME, TransactionType.EXPENSE],
        weights=[30, 70]  # more expenses than income — realistic
    )[0]

    if tx_type == TransactionType.INCOME:
        amount = round(random.uniform(1000, 80000), 2)
        category = random.choice(income_categories)
    else:
        amount = round(random.uniform(50, 8000), 2)
        category = random.choice(expense_categories)

    transactions.append(
        Transaction(
            amount=amount,
            type=tx_type,
            category=category,
            date=today - timedelta(days=random.randint(0, 365)),
            notes=f"Seeded transaction #{i + 1}",
            created_by_id=admin.id,
        )
    )

db.add_all(transactions)
db.commit()
db.close()

print("\n✅  Seed complete!\n")
print("  Username   Password    Role")
print("  ─────────  ──────────  ────────")
print("  admin      admin123    Admin")
print("  analyst    analyst123  Analyst")
print("  viewer     viewer123   Viewer")
print("\nStart the server:  uvicorn app.main:app --reload")
print("API docs:          http://localhost:8000/docs\n")
