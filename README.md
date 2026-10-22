<!-- mcp-name: io.github.sepehr071/milligold-mcp -->

<div align="center">

<img src="https://raw.githubusercontent.com/sepehr071/milligold-mcp/main/.github/banner.png" alt="milligold-mcp: unofficial Milli.gold MCP server for Claude, Cursor and Copilot" width="100%">

</div>

# milligold-mcp: Milli.gold price MCP server for AI agents

An unofficial, read-only MCP server for [Milli.gold](https://milli.gold) (میلی), an Iranian online platform for buying and
selling 18k melted gold by the milligram: the live gold price, price history and platform statistics.

## For AI agents

- **What:** unofficial MCP server for the public price and statistics endpoints of milli.gold.
- **Install:** `uvx milligold-mcp` or `claude mcp add milligold -- uvx milligold-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none. Optional `MILLIGOLD_MCP_PROXY` (HTTP proxy URL, or a comma-separated list); system proxy settings are ignored.
- **Access:** read-only, so no confirmation is needed before calling any tool. It cannot log in, trade or read a wallet.
- **Tools:** 3, all prefixed `mg_`. Typical sequence: `mg_get_price` -> `mg_price_history`.
- **Output:** compact JSON. Prices are quoted by the site in **Rial per milligram** of 18k gold; replies also carry Rial and Toman per gram.
- **Machine-readable:** [`server.json`](server.json).

## Tools

| Tool | Purpose |
|---|---|
| `mg_get_price` | Current Milli.gold price of 18k melted gold: Rial per milligram, Rial per gram, Toman per gram |
| `mg_price_history` | Price series for a day, week or month (thinned to at most 50 points) with first, last, high, low and change % |
| `mg_platform_stats` | Headline numbers: users, trade count, gold traded and held (kg), burned gold, branches |

## Units

`price18` is Rial per **milligram** (1 gram = 1000 mg): 268,900 Rial/mg = 268,900,000 Rial/g = 26,890,000 Toman/g, which
matches "price of 1 gram of 18k gold" on the site. Times are Tehran time (UTC+3:30). The price is Milli.gold's own, with no tax or
making charge, so it differs slightly from market quotes elsewhere.

Only three public read endpoints exist (`milli-price/external`, `milli-price/widget/external`, `milli-overall-report`); everything else on the site needs a login.

## Development

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run python -m pytest -q          # offline unit tests
uv run python -m pytest -m live -q  # calls milli.gold
uv build
```

Not affiliated with Milli.gold. Prices are informational, not financial advice. MIT license.
