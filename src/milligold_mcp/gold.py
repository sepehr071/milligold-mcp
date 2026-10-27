"""Milli.gold tools: live 18k gold price, price history, platform statistics, fees and trade quotes."""

from __future__ import annotations

import html
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Literal

from pydantic import Field

from .http import API, SITE, ApiError, fetch
from .registry import tool

TEHRAN = timezone(timedelta(hours=3, minutes=30))  # no DST since 2022
FEES_PAGE = f"{SITE}/main/commision/"  # sic: the site's own spelling
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٫٬", "0123456789.,")
FEE_ROWS = {  # row label on the fees page -> key
    "واریز": "wallet_deposit",
    "برداشت": "wallet_withdrawal",
    "خرید": "buy",
    "فروش": "sell",
    "انتقال": "transfer",
    "تحویل": "delivery",
    "نگهداری": "storage",
}


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


def _cell(v: str) -> str | None:
    """A fee bound in plain form: '1 mg', '2000 toman', '0', 'none' (no cap); None when the page shows '-'."""
    s = " ".join(v.translate(DIGITS).split())
    if s in ("", "-"):
        return None
    return "none" if s == "ندارد" else s.replace("میلی", "mg").replace("تومان", "toman")


def _percent(v: str) -> float | None:
    try:
        return float(v.translate(DIGITS))
    except ValueError:
        return None


def _mg(v: str | None) -> float:
    m = re.fullmatch(r"([\d.]+) mg", v or "")
    return float(m[1]) if m else 0.0


def _fee_tables(page: str) -> dict[str, dict[str, dict[str, Any]]]:
    """Parse the individual and company fee tables (label, minimum, percent, maximum) from the fees page."""
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for table in re.findall(r"<table.*?</table>", page, re.S):
        rows = [
            [
                html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
            ]
            for r in re.findall(r"<tr.*?</tr>", table, re.S)
        ]
        head = rows[0][0] if rows and len(rows[0]) == 4 else ""
        who = "individual" if "حقیقی" in head else "company" if "حقوقی" in head else None
        if who is None:
            continue
        fees = out.setdefault(who, {})
        for label, low, pct, high in (r for r in rows[1:] if len(r) == 4):
            if key := next((k for word, k in FEE_ROWS.items() if word in label), None):
                fees[key] = {"min": _cell(low), "percent": _percent(pct), "max": _cell(high)}
    if not {"buy", "sell"} <= out.get("individual", {}).keys():
        raise ApiError("Milli.gold fees page has no fee table; the page layout may have changed.")
    return out


@tool("Milli.gold fees")
async def mg_fees(
    customer: Annotated[
        Literal["individual", "company"],
        Field(description="individual = personal account, company = business account."),
    ] = "individual",
) -> dict[str, Any]:
    """Get Milli.gold's current fees for buying, selling, transferring and delivering gold and for wallet withdrawals.

    Read live from the site's fees page. Each fee is `percent` of the amount, but at least `min` and at most `max`
    ('none' = no cap). 'mg' means milligrams of gold. Delivery is physical gold (bars) handed over at a branch.
    To price a concrete trade use mg_trade_quote.
    """
    fees = _fee_tables(await fetch(FEES_PAGE, text=True))
    if customer not in fees:
        raise ApiError(f"Milli.gold fees page has no {customer} table.")
    return {"customer": customer, "source": FEES_PAGE, "fees": fees[customer]}


@tool("Milli.gold trade cost quote")
async def mg_trade_quote(
    side: Annotated[Literal["buy", "sell"], Field(description="buy = you buy gold, sell = you sell gold.")],
    grams: Annotated[
        float | None, Field(description="Amount of 18k gold in grams (e.g. 0.5).", gt=0, le=100_000)
    ] = None,
    toman: Annotated[
        int | None, Field(description="Buy only: total budget in Toman, fee included (e.g. 5000000).", gt=0)
    ] = None,
) -> dict[str, Any]:
    """Estimate what a gold trade on Milli.gold costs or pays out right now, fee included, at the live price.

    Give `grams` for a buy or a sale, or `toman` (a budget, fee included) for a buy. The fee follows the fees page:
    the larger of `min` and `percent` of the amount (today 1 mg or 0.5 %). `pay_toman` is the total for a buy,
    `receive_toman` the payout of a sale. It is an estimate: new-user fee waivers and wallet withdrawal fees are not
    applied, and the price moves. For the fee table itself use mg_fees.
    """
    if (grams is None) == (toman is None):
        raise ApiError("Give exactly one of grams or toman.")
    if side == "sell" and toman is not None:
        raise ApiError("For a sale give grams; toman is a buying budget.")
    d = _data(await fetch(f"{API}/milli-price/external"), "price")
    if not isinstance(d.get("price18"), int | float) or d["price18"] <= 0:
        raise ApiError("Milli.gold returned no price.")
    fee = _fee_tables(await fetch(FEES_PAGE, text=True))["individual"][side]
    toman_per_mg = d["price18"] / 10
    rate, floor = (fee["percent"] or 0) / 100, _mg(fee["min"])
    if toman is not None:
        total_mg = toman / toman_per_mg  # gold plus fee
        gold = total_mg / (1 + rate) if total_mg * rate / (1 + rate) >= floor else max(total_mg - floor, 0)
    else:
        gold = grams * 1000
    fee_mg = max(floor, gold * rate)
    value, fee_toman = gold * toman_per_mg, fee_mg * toman_per_mg
    total = (
        {"pay_toman": round(value + fee_toman)}
        if side == "buy"
        else {"receive_toman": max(round(value - fee_toman), 0)}
    )
    return {
        "side": side,
        "as_of": d.get("date"),
        "toman_per_gram": d["price18"] * 100,
        "gold_mg": round(gold, 1),
        "value_toman": round(value),
        "fee_mg": round(fee_mg, 2),
        "fee_toman": round(fee_toman),
        "fee_rule": f"max({fee['min']}, {fee['percent']} %)",
        **total,
    }
