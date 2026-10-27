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


async def test_live_fees_and_quote(client):
    fees = (await client.call_tool("mg_fees", {})).structured_content["fees"]
    assert fees["buy"]["percent"] is not None
    r = (await client.call_tool("mg_trade_quote", {"side": "buy", "grams": 1})).structured_content
    assert r["pay_toman"] > r["value_toman"] > 1_000_000


async def test_live_posts_help_and_read(client):
    for section in ("news", "mag", "help"):
        posts = (await client.call_tool("mg_latest_posts", {"section": section, "limit": 3})).structured_content[
            "posts"
        ]
        assert len(posts) == 3 and all(p["url"].startswith(f"https://milli.gold/{section}/") for p in posts)
    topics = (await client.call_tool("mg_help_topics", {"query": "fee"})).structured_content["topics"]
    assert topics
    r = (await client.call_tool("mg_read", {"url": topics[0]["url"]})).structured_content
    assert r["title"] and len(r["text"]) > 200
