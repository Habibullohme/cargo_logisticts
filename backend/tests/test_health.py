from datetime import datetime


async def test_health_ok(client, db_ok):
    resp = await client.get("/api/v1/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["message"] == "Assalomu alaykum! Server ishlayapti."


async def test_health_reports_database_down(client, db_ok):
    db_ok["ok"] = False

    body = (await client.get("/api/v1/health")).json()

    assert body["status"] == "degraded"
    assert body["database"] == "error"
    assert body["database_message"] == "Baza bilan aloqa yo'q"


async def test_health_server_time_is_tashkent(client, db_ok):
    body = (await client.get("/api/v1/health")).json()

    server_time = datetime.fromisoformat(body["server_time"])
    assert server_time.utcoffset().total_seconds() == 5 * 3600
