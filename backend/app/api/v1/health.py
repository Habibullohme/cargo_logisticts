"""Tekshiruv so'rovi: bot, sayt va ilova server bilan aloqani shu orqali sinaydi."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.db import check_database
from app.core.timezone import now_tashkent
from app.i18n import t

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: str
    message: str
    database: str
    database_message: str
    server_time: str
    version: str


async def database_checker() -> bool:
    return await check_database()


@router.get("/health", response_model=HealthOut)
async def health(db_ok: bool = Depends(database_checker)) -> HealthOut:
    return HealthOut(
        status="ok" if db_ok else "degraded",
        message=t("health.hello"),
        database="ok" if db_ok else "error",
        database_message=t("health.db_ok" if db_ok else "health.db_error"),
        server_time=now_tashkent().isoformat(timespec="seconds"),
        version=get_settings().app_version,
    )
