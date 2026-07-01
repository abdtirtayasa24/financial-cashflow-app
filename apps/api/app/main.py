from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.models import CurrentUser
from app.modules.app_settings.router import router as settings_router
from app.modules.attachments.router import router as attachments_router
from app.modules.cash_accounts.router import router as cash_accounts_router
from app.modules.cashflow_categories.router import router as categories_router
from app.modules.departments.router import router as departments_router
from app.modules.payment_methods.router import router as payment_methods_router
from app.modules.transactions.router import router as transactions_router
from app.modules.users.router import router as users_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(AppError, app_error_handler)


core_router = APIRouter(tags=["Auth"])


@core_router.get("/me", response_model=CurrentUser)
async def me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    return current_user


app.include_router(core_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(departments_router, prefix=settings.api_prefix)
app.include_router(categories_router, prefix=settings.api_prefix)
app.include_router(payment_methods_router, prefix=settings.api_prefix)
app.include_router(cash_accounts_router, prefix=settings.api_prefix)
app.include_router(settings_router, prefix=settings.api_prefix)
app.include_router(transactions_router, prefix=settings.api_prefix)
app.include_router(attachments_router, prefix=settings.api_prefix)


@app.get(f"{settings.api_prefix}/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}