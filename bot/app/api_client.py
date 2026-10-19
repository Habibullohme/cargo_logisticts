"""Backend API bilan gaplashish. Bot bazaga to'g'ridan-to'g'ri ulanmaydi."""

import httpx

from app.config import get_settings


class ApiClient:
    def __init__(
        self, base_url: str | None = None, transport: httpx.AsyncBaseTransport | None = None
    ):
        settings = get_settings()
        headers = {"X-Bot-Key": settings.bot_api_key} if settings.bot_api_key else {}
        self._client = httpx.AsyncClient(
            base_url=base_url or settings.api_url,
            headers=headers,
            timeout=10,
            transport=transport,
        )

    async def health(self) -> dict:
        resp = await self._client.get("/api/v1/health")
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._client.aclose()
