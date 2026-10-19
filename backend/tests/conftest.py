import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.health import database_checker
from app.main import app


@pytest.fixture
def db_ok():
    """Testlarda haqiqiy baza shart emas: baza holatini o'zimiz belgilaymiz."""
    state = {"ok": True}

    async def fake_checker() -> bool:
        return state["ok"]

    app.dependency_overrides[database_checker] = fake_checker
    yield state
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
