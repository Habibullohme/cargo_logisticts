import httpx

from app.api_client import ApiClient
from app.handlers.start import server_status_text

HEALTH_OK = {
    "status": "ok",
    "message": "Assalomu alaykum! Server ishlayapti.",
    "database": "ok",
    "database_message": "Baza bilan aloqa bor",
    "server_time": "2026-10-19T09:05:00+05:00",
    "version": "0.1.0",
}


def test_status_text_ok():
    text = server_status_text(HEALTH_OK)
    assert "Server bilan aloqa bor" in text
    assert "09:05, 19.10.2026" in text


def test_status_text_db_down():
    text = server_status_text({**HEALTH_OK, "database": "error"})
    assert "baza bilan aloqa yo'q" in text


def test_status_text_server_down():
    assert "server bilan aloqa yo'q" in server_status_text(None)


async def test_api_client_calls_health_endpoint():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/health"
        return httpx.Response(200, json=HEALTH_OK)

    api = ApiClient(base_url="http://backend", transport=httpx.MockTransport(handler))
    assert await api.health() == HEALTH_OK
    await api.close()
