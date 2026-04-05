# Finance Dashboard API

A backend for a multi-role finance dashboard system, built with **FastAPI** and **SQLite**.

---

## Tech Stack

| Layer       | Choice                              | Why                                             |
|-------------|-------------------------------------|-------------------------------------------------|
| Framework   | FastAPI                             | Fast, async-ready, auto-generates OpenAPI docs  |
| Database    | SQLite via SQLAlchemy ORM           | Zero setup, easy to swap out for Postgres later |
| Auth        | JWT (via `python-jose`)             | Stateless — scales easily, no session storage   |
| Passwords   | bcrypt (via `passlib`)              | Industry standard for secure hashing            |
| Validation  | Pydantic v2                         | Automatic, schema-driven request validation     |

---

## Project Structure

```
finance_backend/
├── app/
│   ├── main.py               # App entry point, middleware, router registration
│   ├── config.py             # Settings loaded from env variables
│   ├── database.py           # SQLAlchemy engine + session setup
│   ├── models/
│   │   ├── user.py           # User ORM model + UserRole enum
│   │   └── transaction.py    # Transaction ORM model + TransactionType enum
│   ├── schemas/
│   │   ├── user.py           # Pydantic schemas for user input/output
│   │   ├── transaction.py    # Pydantic schemas for transaction input/output
│   │   └── auth.py           # Login request + token response schemas
│   ├── routers/
│   │   ├── auth.py           # /auth/register, /auth/login
│   │   ├── users.py          # /users CRUD
│   │   ├── transactions.py   # /transactions CRUD + filters
│   │   └── dashboard.py      # /dashboard summary, trends, categories
│   ├── services/
│   │   ├── auth_service.py        # register + login logic
│   │   ├── user_service.py        # user CRUD business logic
│   │   ├── transaction_service.py # transaction CRUD + filter logic
│   │   └── dashboard_service.py   # analytics + aggregation queries
│   └── core/
│       ├── security.py       # JWT creation/decoding, password hashing
│       ├── exceptions.py     # Custom exception hierarchy
│       └── dependencies.py   # FastAPI auth dependencies + role guards
├── seed.py                   # Populate DB with demo users and transactions
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Seed demo data (optional but recommended)

```bash
python seed.py
```

This creates three demo accounts:

| Username | Password   | Role    |
|----------|------------|---------|
| admin    | admin123   | Admin   |
| analyst  | analyst123 | Analyst |
| viewer   | viewer123  | Viewer  |

### 3. Start the server

```bash
uvicorn app.main:app --reload
```

### 4. Open the interactive API docs

```
http://localhost:8000/docs
```

---

## Authentication

All endpoints (except `/auth/register` and `/auth/login`) require a Bearer token.

**Step 1 — Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Step 2 — Use the token:**
```bash
curl http://localhost:8000/dashboard/summary \
  -H "Authorization: Bearer <your_token_here>"
```

---

## API Reference

### Auth

| Method | Endpoint         | Description                  | Auth required |
|--------|------------------|------------------------------|---------------|
| POST   | /auth/register   | Create a new user account    | No            |
| POST   | /auth/login      | Get a JWT token              | No            |

### Users

| Method | Endpoint         | Description                        | Roles allowed        |
|--------|------------------|------------------------------------|----------------------|
| GET    | /users/me        | View your own profile              | All                  |
| GET    | /users/          | List all users                     | Admin                |
| GET    | /users/{id}      | View a specific user               | Admin, or self       |
| PATCH  | /users/{id}      | Update role / email / status       | Admin                |
| DELETE | /users/{id}      | Permanently delete a user          | Admin                |

### Transactions

| Method | Endpoint              | Description                             | Roles allowed        |
|--------|-----------------------|-----------------------------------------|----------------------|
| POST   | /transactions/        | Create a transaction                    | Analyst, Admin       |
| GET    | /transactions/        | List transactions (with filters)        | All                  |
| GET    | /transactions/{id}    | View a single transaction               | All                  |
| PATCH  | /transactions/{id}    | Update a transaction                    | Analyst, Admin       |
| DELETE | /transactions/{id}    | Soft-delete a transaction               | Admin                |

**Transaction filters (query params):**
- `type` — `income` or `expense`
- `category` — partial text match
- `date_from` / `date_to` — date range (`YYYY-MM-DD`)
- `page` / `page_size` — pagination

### Dashboard

| Method | Endpoint               | Description                                    | Roles allowed |
|--------|------------------------|------------------------------------------------|---------------|
| GET    | /dashboard/summary     | Total income, expenses, net balance, count     | All           |
| GET    | /dashboard/categories  | Per-category totals split by income/expense    | All           |
| GET    | /dashboard/trends      | Monthly income vs expense (12 months, any year)| All           |
| GET    | /dashboard/recent      | Most recent N transactions                     | All           |

---

## Role Permissions Summary

| Action                          | Viewer | Analyst | Admin |
|---------------------------------|--------|---------|-------|
| View transactions & dashboard   | ✅     | ✅      | ✅    |
| Create / edit transactions      | ❌     | ✅      | ✅    |
| Delete transactions (soft)      | ❌     | ❌      | ✅    |
| View user list                  | ❌     | ❌      | ✅    |
| Update user roles/status        | ❌     | ❌      | ✅    |
| Delete users                    | ❌     | ❌      | ✅    |

---

## Design Decisions & Assumptions

**Layered architecture (Router → Service → Model)**
Routes only handle HTTP concerns. Business logic lives in services. This makes the code easier to test and maintain.

**Soft delete on transactions**
Deleted transactions are marked `is_deleted = True` rather than removed. This preserves financial history and makes accidental-delete recovery possible — important for any real finance system.

**Custom exception hierarchy**
All errors extend `FinanceAPIError` which extends `HTTPException`. A central handler in `main.py` ensures every error returns consistent JSON (`{"detail": "..."}`), regardless of where in the code it's thrown.

**`require_roles()` dependency factory**
Role enforcement is done via a reusable factory function rather than repeating logic in every route. This means adding a new role or changing permissions requires one change in one place.

**JWT embeds role**
The user's role is stored inside the JWT payload. This means basic role checks don't need a database hit — the token carries enough information.

**All 12 months in trends**
`/dashboard/trends` always returns a full 12-entry list (zeroed out for months with no data) so a frontend chart can render without handling missing data points.

**SQLite for simplicity**
SQLite is used for easy local setup. The `DATABASE_URL` setting in `config.py` (or `.env`) can be changed to a Postgres URL and the rest of the code works without modification.

**Assumption: any admin can register users with any role**
In a real product, you'd probably restrict analyst/admin role assignment to existing admins. This is documented as a known simplification.

---

## Running Without the Seed Script

If you prefer to start fresh:

1. Start the server: `uvicorn app.main:app --reload`
2. Register an admin: `POST /auth/register` with `"role": "admin"`
3. Login to get a token: `POST /auth/login`
4. Use the token for all subsequent requests
