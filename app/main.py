from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import FinanceAPIError
from app.database import Base, engine
from app.routers import auth, dashboard, transactions, users

# Create all DB tables on startup if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="""
## Finance Dashboard API

A backend for a multi-role finance management system.

### Roles
| Role     | Permissions |
|----------|-------------|
| viewer   | Read-only access to transactions and dashboard |
| analyst  | Read + create/edit transactions |
| admin    | Full access including user management |

### Quick Start
1. Register a user via `POST /auth/register`
2. Login via `POST /auth/login` to get a token
3. Use the token as `Authorization: Bearer <token>` in all other requests

Or run `python seed.py` to load demo data with pre-built users.
    """,
    contact={"name": "Finance API"},
)

# Allow all origins in development — tighten this in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FinanceAPIError)
async def finance_exception_handler(request: Request, exc: FinanceAPIError):
    """
    Centralised error handler for all our custom exceptions.
    Returns consistent JSON: {"detail": "..."} for every error.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Register all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def health_check():
    """Quick check to confirm the API is running."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
    }
