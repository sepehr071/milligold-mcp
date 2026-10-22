"""Milli.gold tools: live 18k gold price, price history, platform statistics."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

from pydantic import Field

from .http import API, ApiError, fetch
from .registry import tool

TEHRAN = timezone(timedelta(hours=3, minutes=30))  # no DST since 2022


def _data(body: Any, what: str) -> dict[str, Any]:
    data = body.get("data") if isinstance(body, dict) else None
    if not isinstance(body, dict) or body.get("code") != 0 or not isinstance(data, dict):
        raise ApiError(f"Milli.gold returned no {what}.")
    return data


def _price(rial_per_mg: int) -> dict[str, Any]:
    return {
        "rial_per_mg": rial_per_mg,
        "rial_per_gram": rial_per_mg * 1000,
        "toman_per_gram": rial_per_mg * 100,
    }


@tool("Milli.gold live gold price")
async def mg_get_price() -> dict[str, Any]:
    """Get the current Milli.gold price of 18k melted gold, in Rial per milligram and per gram.

    Milli.gold sells gold by the milligram (1 gram = 1000 mg); the quote is the platform's own price
    with no tax or making charge. `as_of` is Tehran time. For the trend over a day, week or month use
    mg_price_history.
    """
    d = _data(await fetch(f"{API}/milli-price/external"), "price")
    if not isinstance(d.get("price18"), int | float):
        raise ApiError("Milli.gold returned no price.")
    return {"as_of": d.get("date"), **_price(d["price18"]), "karat": 18}


@tool("Milli.gold price history")
async def mg_price_history(
    period: Annotated[
        Literal["DAILY", "WEEKLY", "MONTHLY"],
        Field(description="Window: DAILY = last ~24 h (15-min points), WEEKLY = last week, MONTHLY = last ~month."),
    ] = "DAILY",
    points: Annotated[int, Field(description="Max points to return, evenly spaced (2-50).", ge=2, le=50)] = 24,
) -> dict[str, Any]:
    """Get the Milli.gold 18k gold price series for a day, week or month, with high, low and change.

    Prices are Rial per milligram; `time` is Tehran time. Points are thinned evenly to `points`.
    """
    prices = _data(await fetch(f"{API}/milli-price/widget/external"), "price history").get("prices")
    series = prices.get(period) if isinstance(prices, dict) else None
    if not series or not all(isinstance(p, dict) and p.get("timestamp") and p.get("value") for p in series):
        raise ApiError(f"Milli.gold returned no {period} history.")
    series = sorted(series, key=lambda p: p["timestamp"])
    # Like the site: stats span every series from this window's start (the day's peak counts in the week) plus the live price.
    every = [
        p
        for v in prices.values()
        if isinstance(v, list)
        for p in v
        if isinstance(p, dict) and p.get("value") and p.get("timestamp", 0) >= series[0]["timestamp"]
    ]
    values = [p["value"] for p in sorted(every, key=lambda p: p["timestamp"])]
    try:
        values.append(_data(await fetch(f"{API}/milli-price/external"), "price")["price18"])
    except (ApiError, KeyError):
        pass  # live price is a refinement; the series alone is still valid
    step = (len(series) - 1) / (points - 1)
    picked = [series[round(i * step)] for i in range(min(points, len(series)))] if len(series) > points else series
    first, last = values[0], values[-1]
    return {
        "period": period,
        "unit": "rial_per_mg",
        "first": first,
        "last": last,
        "high": max(values),
        "low": min(values),
        "change_percent": round((last - first) / first * 100, 2),
        "points": [
            {
                "time": datetime.fromtimestamp(p["timestamp"] / 1000, TEHRAN).strftime("%Y-%m-%d %H:%M"),
                "price": p["value"],
            }
            for p in picked
        ],
    }


@tool("Milli.gold platform statistics")
async def mg_platform_stats() -> dict[str, Any]:
    """Get Milli.gold's headline numbers: users, trades, gold traded, gold held and branches.

    Figures are rounded totals the company publishes; weights are in kilograms. For prices use mg_get_price.
    """
    d = _data(await fetch(f"{API}/milli-overall-report"), "statistics")
    return {
        "users": d.get("overallNumberOfUsers"),
        "trade_transactions": d.get("overallNumberOfTradeTransactions"),
        "traded_gold_kg": d.get("overallTradedMilliTurnoverInKg"),
        "user_balances_kg": d.get("overallUsersMilliBalanceInKg"),
        "burned_kg": d.get("overallBurnedMilliAmountInKg"),
        "branches_and_representatives": d.get("numberOfBranchesAndRepresentatives"),
    }
