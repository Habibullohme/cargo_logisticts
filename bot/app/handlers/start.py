from datetime import datetime

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.api_client import ApiClient
from app.i18n import t

router = Router()


def server_status_text(health: dict | None) -> str:
    """Backend javobidan foydalanuvchiga tushunarli matn."""
    if health is None:
        return t("start.server_error")
    if health.get("database") != "ok":
        return t("start.server_db_error")
    time = datetime.fromisoformat(health["server_time"]).strftime("%H:%M, %d.%m.%Y")
    return t("start.server_ok", message=health["message"], time=time)


@router.message(CommandStart())
async def cmd_start(message: Message, api: ApiClient) -> None:
    name = message.from_user.first_name if message.from_user else t("start.friend")
    await message.answer(t("start.greeting", name=name))

    try:
        health = await api.health()
    except Exception:
        health = None
    await message.answer(server_status_text(health))
