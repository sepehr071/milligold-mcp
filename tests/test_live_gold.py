import pytest

pytestmark = [pytest.mark.live, pytest.mark.anyio]


async def test_live_price(client):
    r = (await client.call_tool("mg_get_price", {})).structured_content
    assert r["rial_per_gram"] > 1_000_000 and r["rial_per_gram"] == r["rial_per_mg"] * 1000


async def test_live_history(client):
    for period in ("DAILY", "WEEKLY", "MONTHLY"):
        r = (await client.call_tool("mg_price_history", {"period": period, "points": 10})).structured_content
        assert len(r["points"]) == 10 and r["low"] <= r["high"]


async def test_live_stats(client):
    r = (await client.call_tool("mg_platform_stats", {})).structured_content
    assert r["users"] > 1_000_000
