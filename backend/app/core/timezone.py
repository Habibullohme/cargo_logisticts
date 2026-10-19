"""Vaqt bilan ishlash. Bazada UTC, foydalanuvchiga Asia/Tashkent."""

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

TASHKENT = ZoneInfo("Asia/Tashkent")


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_tashkent() -> datetime:
    return datetime.now(TASHKENT)


def today_tashkent() -> date:
    """ "Bugun" — Toshkent sanasi bo'yicha (server qaysi zonada bo'lishidan qat'i nazar)."""
    return now_tashkent().date()
