import httpx
import pytest
from conftest import fixture

from milligold_mcp import http

pytestmark = pytest.mark.anyio

P = "/api/v1/public"


async def test_all_tools_are_read_only(client):
    tools = (await client.list_tools()).tools
    assert {t.name for t in tools} == {"mg_get_price", "mg_price_history", "mg_platform_stats"}
    for t in tools:
        assert t.annotations.read_only_hint is True, t.name
        assert t.description and t.title, t.name


async def test_get_price_units(client, api):
    api[f"{P}/milli-price/external"] = fixture("price.json")
    r = (await client.call_tool("mg_get_price", {})).structured_content
    assert r["rial_per_mg"] == 268900
    assert r["rial_per_gram"] == 268_900_000 and r["toman_per_gram"] == 26_890_000
    assert r["as_of"].startswith("2026-10-22")


async def test_price_history_thins_and_summarises(client, api):
    api[f"{P}/milli-price/widget/external"] = fixture("widget.json")
    r = (await client.call_tool("mg_price_history", {"period": "WEEKLY", "points": 5})).structured_content
    assert len(r["points"]) == 5 and r["low"] <= r["last"] <= r["high"]
    assert r["points"][0]["price"] == r["first"]


async def test_price_history_rejects_bad_period(client, api):
    api[f"{P}/milli-price/widget/external"] = fixture("widget.json")
    assert (await client.call_tool("mg_price_history", {"period": "YEARLY"})).is_error


async def test_platform_stats(client, api):
    api[f"{P}/milli-overall-report"] = fixture("report.json")
    r = (await client.call_tool("mg_platform_stats", {})).structured_content
    assert r["users"] == 27_000_000 and r["branches_and_representatives"] == 16


async def test_cookie_redirect_is_retried(client, api):
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) == 1:
            return httpx.Response(307, headers={"location": str(request.url)})
        return httpx.Response(200, json=fixture("price.json"))

    api[f"{P}/milli-price/external"] = handler
    r = await client.call_tool("mg_get_price", {})
    assert not r.is_error and len(calls) == 2


async def test_http_error_is_tool_error(client, api):
    api[f"{P}/milli-overall-report"] = lambda r: httpx.Response(403)
    r = await client.call_tool("mg_platform_stats", {})
    assert r.is_error and "403" in r.content[0].text


@pytest.mark.parametrize(
    "tool, path, body",
    [
        ("mg_get_price", "milli-price/external", [1]),
        ("mg_get_price", "milli-price/external", {"code": 0, "data": {"date": "x"}}),
        ("mg_price_history", "milli-price/widget/external", {"code": 0, "data": {"prices": None}}),
        ("mg_price_history", "milli-price/widget/external", {"code": 0, "data": {"prices": {"DAILY": [{"value": 1}]}}}),
    ],
)
async def test_malformed_reply_gives_clear_error(client, api, tool, path, body):
    api[f"{P}/{path}"] = lambda r: httpx.Response(200, json=body)
    r = await client.call_tool(tool, {})
    assert r.is_error and "Milli.gold returned no" in r.content[0].text


async def test_week_stats_include_day_peak_and_live_price(client, api):
    day = [{"timestamp": 2000, "value": 130}, {"timestamp": 3000, "value": 110}]
    week = [{"timestamp": 1000, "value": 100}, {"timestamp": 2500, "value": 120}]
    api[f"{P}/milli-price/widget/external"] = lambda r: httpx.Response(
        200, json={"code": 0, "data": {"prices": {"DAILY": day, "WEEKLY": week}}}
    )
    api[f"{P}/milli-price/external"] = lambda r: httpx.Response(200, json={"code": 0, "data": {"price18": 150}})
    r = (await client.call_tool("mg_price_history", {"period": "WEEKLY"})).structured_content
    assert (r["first"], r["last"], r["high"], r["low"], r["change_percent"]) == (100, 150, 150, 100, 50.0)
    api[f"{P}/milli-price/external"] = lambda r: httpx.Response(500)
    http._cache.clear()
    r = (await client.call_tool("mg_price_history", {"period": "WEEKLY"})).structured_content
    assert r["high"] == 130 and r["last"] == 110
