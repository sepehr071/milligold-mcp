<!-- mcp-name: io.github.sepehr071/milligold-mcp -->

<div align="center">

<img src="https://raw.githubusercontent.com/sepehr071/milligold-mcp/main/.github/banner.png" alt="milligold-mcp: unofficial Milli.gold MCP server for Claude, Cursor and Copilot" width="100%">

# milligold-mcp: Milli.gold price MCP server for AI agents

**Give your AI agent the live 18k gold price from Milli.gold (میلی).**<br>
An unofficial, read-only MCP server for [Milli.gold](https://milli.gold), an Iranian online platform for 18k gold sold by the milligram:<br>
the live gold price per gram, day, week and month price history, and platform statistics, all from Claude, Cursor or Copilot.

[![PyPI](https://img.shields.io/pypi/v/milligold-mcp?color=2563eb)](https://pypi.org/project/milligold-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/milligold-mcp)](https://pypi.org/project/milligold-mcp/)
[![CI](https://github.com/sepehr071/milligold-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sepehr071/milligold-mcp/actions/workflows/ci.yml)
[![MCP Registry](https://img.shields.io/badge/MCP_Registry-io.github.sepehr071%2Fmilligold--mcp-7c3aed)](https://registry.modelcontextprotocol.io/?q=milligold-mcp)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/milligold-mcp/blob/main/LICENSE)
[![mcpfarsi](https://mcpfarsi.ir/badge/milligold.svg)](https://mcpfarsi.ir/servers/milligold/)

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=milligold&config=eyJjb21tYW5kIjoidXZ4IiwiYXJncyI6WyJtaWxsaWdvbGQtbWNwIl19)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_milligold--mcp-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=milligold&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22milligold-mcp%22%5D%7D)

[For AI agents](#for-ai-agents) · [Quick start](#quick-start) · [What it can do](#what-it-can-do) · [Tools](#tools) · [Good to know](#good-to-know) · [FAQ](#faq) · [فارسی](#فارسی)

</div>

---

## For AI agents

- **What:** unofficial MCP server (model context protocol) for the public price, statistics, fees, news and help pages of milli.gold. A gold price API for Iran in tool form.
- **Install:** `uvx milligold-mcp` or `claude mcp add milligold -- uvx milligold-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none, no API key or account. Optional `MILLIGOLD_MCP_PROXY` (HTTP proxy URL, or a comma-separated list); system proxy settings are ignored.
- **Access:** read-only, so no confirmation is needed before calling any tool. It cannot log in, trade or read a wallet.
- **Tools:** 8, all prefixed `mg_`. Typical sequences: `mg_get_price` -> `mg_price_history`; `mg_trade_quote`; `mg_latest_posts` or `mg_help_topics` -> `mg_read`.
- **Use when:** the user asks for the current 18k gold price per gram on Milli.gold, how it moved over a day, week or month, what a buy or sale costs with fees, Milli.gold's fees, its latest gold news, or how to use Milli (delivery, transfer, verification).
- **Do not use when:** the user wants to actually buy or sell gold, needs a market-wide quote, or wants dollar, coin or crypto prices (see [tgju-mcp](https://github.com/sepehr071/tgju-mcp)).
- **Output:** compact JSON. Milli.gold quotes **Rial per milligram** of 18k gold; replies also carry Rial per gram and Toman per gram. Times are Tehran time.
- **Machine-readable:** [`server.json`](https://github.com/sepehr071/milligold-mcp/blob/main/server.json) and the
  [iran-mcp catalog](https://github.com/sepehr071/iran-mcp) (`TOOLS.md`, `servers.json`, `llms.txt`).

## Why

Milli.gold sells 18k melted gold by the milligram, so its price is quoted per milligram, in Rial. The site shows the
price per gram, and the numbers are easy to misread by a factor of 10 or 1000. An agent with `milligold-mcp` reads
the quote straight from the public endpoints and does the unit conversion for you:

> **You:** What is the Milli.gold gold price right now, and is it up or down this week?
>
> **Agent:** *calls* `mg_get_price()` -> `mg_price_history(period="WEEKLY")`
>
> One gram of 18k gold costs 26,890,000 Toman on Milli.gold (268,900 Rial per milligram). Over the past week it
> moved by the percentage shown in `change_percent`, between the week's low and high.

<sub>Illustrative example with the price from the site's own unit explanation; prices change all the time.</sub>

## What it can do

- **Live price** of 18k gold on Milli.gold: Rial per milligram, Rial per gram and Toman per gram, with the Tehran-time timestamp
- **Price history** for the last day, week or month, with first, last, high, low and change percent
- **Platform statistics**: users, trade transactions, gold traded and held (kg), burned gold (kg), branches and representatives
- **Fees** for buying, selling, transferring and delivering gold and for wallet withdrawals, read live from the fees page
- **Trade quotes**: what buying N grams (or spending a Toman budget) costs, or what selling pays, fee included
- **News, magazine and help**: the newest posts (daily gold, ounce and market reports), help articles found by keyword, and the full text of any post
- **Read-only by design**: no login, no trading, no wallet

Example prompts:

- "What is the 18k gold price per gram on Milli.gold right now?"
- "Show me Milli.gold's gold price for the last month. What were the high and the low?"
- "Is gold up or down today on Milli.gold? Give me the change in percent."
- "How many users and how much gold does Milli.gold report?"
- "How much do I pay on Milli.gold for 2 grams of gold, fee included?"
- "How do I get physical gold delivered from Milli, and what does it cost?"
- <span dir="rtl">با ۵ میلیون تومان چند میلی طلا در میلی می&zwnj;توانم بخرم؟</span>
- <span dir="rtl">آخرین اخبار قیمت طلا در میلی چیست؟</span>
- <span dir="rtl">قیمت طلای ۱۸ عیار در میلی الان هر گرم چند تومان است؟</span>
- <span dir="rtl">نمودار قیمت طلا در میلی در یک هفته گذشته چطور بوده؟</span>
- <span dir="rtl">امروز قیمت طلا در میلی بالا رفته یا پایین آمده؟</span>

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). No API key or account.

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add milligold -- uvx milligold-mcp
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Settings → Developer → Edit Config, then add:

```json
{
  "mcpServers": {
    "milligold": { "command": "uvx", "args": ["milligold-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

Click **Install in Cursor** above, or add the Claude Desktop block to `~/.cursor/mcp.json`.
</details>

<details>
<summary><b>VS Code (Copilot agent mode)</b></summary>

Click **Install in VS Code** above, or add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "milligold": { "type": "stdio", "command": "uvx", "args": ["milligold-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

```bash
codex mcp add milligold -- uvx milligold-mcp
```

Or add to `~/.codex/config.toml`:

```toml
[mcp_servers.milligold]
command = "uvx"
args = ["milligold-mcp"]
```
</details>

<details>
<summary><b>Gemini CLI</b></summary>

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "milligold": { "command": "uvx", "args": ["milligold-mcp"] }
  }
}
```
</details>

<details>
<summary><b>Windsurf</b></summary>

Add the Claude Desktop block to `~/.codeium/windsurf/mcp_config.json`.
</details>

<details>
<summary><b>Anything else</b></summary>

It's a standard stdio MCP server: run `uvx milligold-mcp`, or `pip install milligold-mcp` and run `milligold-mcp`.
</details>

## Tools

All 8 tools are read-only and return compact JSON.

| Tool | What it does |
|---|---|
| `mg_get_price` | Gets the current Milli.gold price of 18k melted gold in Rial per milligram, Rial per gram and Toman per gram, with the Tehran-time timestamp |
| `mg_price_history` | Gets the 18k gold price series for a day, week or month (`period`: `DAILY`, `WEEKLY`, `MONTHLY`; `points`: 2-50, default 24) with first, last, high, low and change percent |
| `mg_platform_stats` | Gets Milli.gold's headline numbers: users, trade transactions, gold traded (kg), user balances (kg), burned gold (kg), branches and representatives |
| `mg_fees` | Gets the current fees for buying, selling, transferring and delivering gold and for wallet withdrawals (`customer`: `individual` or `company`), each as percent with minimum and maximum |
| `mg_trade_quote` | Estimates the cost of a buy or the payout of a sale at the live price, fee included (`side`: `buy` or `sell`; `grams`, or `toman` as a buying budget) |
| `mg_latest_posts` | Lists the newest posts with date, categories, summary and URL (`section`: `news`, `mag` or `help`; `limit`: 1-20) |
| `mg_help_topics` | Finds help-center articles by English keyword (e.g. `delivery`, `fee`, `card`); empty query lists all |
| `mg_read` | Reads the text of one milli.gold news, magazine or help post (`url`; `max_chars`: 500-20000, default 6000) |

## How it works

```text
  AI agent  (Claude, Cursor, Copilot, ...)
      │
      │  MCP over stdio
      ▼
  milligold-mcp  (runs on your machine)
      │
      │  HTTPS
      └──────▶  milli.gold   price, price history, platform report, fees page, RSS feeds, help sitemap, posts
```

`milligold-mcp` runs locally and reads public, login-free parts of milli.gold: three JSON endpoints (live price,
price widget series, overall report), the fees page, the news, magazine and help RSS feeds, the help sitemap and the
post pages. There is no hosted server in between and no API key.

- **Chrome-like client.** Requests go through a Chrome-impersonating HTTP client, because the site sits behind ArvanCloud.
- **ArvanCloud 307 + cookie.** ArvanCloud sometimes answers with a redirect to the same URL plus a cookie. The server retries once and keeps the cookie, so you never see it.
- **15 s cache.** Repeated calls within 15 seconds reuse the answer instead of hitting the site again.
- **Read-only.** Only GET requests, only to milli.gold. System proxy variables are ignored on purpose.

## Good to know

- **Units.** The site quotes `price18` in **Rial per milligram**, and 1 gram = 1000 mg. So 268,900 Rial/mg x 1000 = 268,900,000 Rial/g, and Rial / 10 = 26,890,000 Toman/g, which matches "price of 1 gram of 18k gold" on the site.
- **Tehran time.** `as_of` and history `time` values are Tehran time (UTC+3:30).
- **Milli.gold's own price.** It is the platform's quote for 18k melted gold, with no tax or making charge. It is not a market-wide quote and not the tgju price, so expect small differences from other sources.
- **History stats follow the site.** The high, low and change for a week or a month include the day's peak and the live price, like the Milli.gold page does. `points` only thins the returned series; it does not change the stats.
- **Statistics are rounded totals** that the company publishes, with weights in kilograms.
- **Trade quotes are estimates.** The fee is the larger of the minimum and the percent on the fees page (today 1 mg or 0.5 %). New-user fee waivers and wallet withdrawal fees are not applied, and the price moves between the quote and a real trade.
- **Posts.** Only the newest posts are available (about 20 news, 10 magazine, 10 help); the site's feeds have no search or older pages. Help articles are found by the English words in their URLs. Post text is Persian.
- **What it does not do.** No buying or selling, no login, no wallet or account data.

## FAQ

<details>
<summary><b>Is there a Milli.gold API or MCP server for AI agents?</b></summary>

Yes: `milligold-mcp` is an unofficial MCP server with 8 read-only tools. It calls the public price and statistics
endpoints and reads the public fees, news and help pages that milli.gold itself serves; no API key is needed.
</details>

<details>
<summary><b>How do I get the 18k gold price per gram in Claude, Cursor or Copilot?</b></summary>

Add the server with `claude mcp add milligold -- uvx milligold-mcp` (or the matching config in
[Quick start](#quick-start)), then ask "What is the 18k gold price per gram on Milli.gold?" in English or Persian.
</details>

<details>
<summary><b>What is the unit of the price?</b></summary>

Milli.gold quotes Rial per milligram. Every reply also carries Rial per gram (x 1000) and Toman per gram (Rial per gram / 10).
</details>

<details>
<summary><b>How is it different from tgju-mcp, and which should I use?</b></summary>

[tgju-mcp](https://github.com/sepehr071/tgju-mcp) reads tgju.org: dollar, euro, gold, coins, crypto and commodity
prices across the Iranian market. `milligold-mcp` reads one platform, Milli.gold, and gives that platform's own gold
price per milligram and its history. Use tgju-mcp for market rates and wide comparisons; use milligold-mcp when the
question is about the price on Milli.gold specifically.
</details>

<details>
<summary><b>Can it buy or sell gold for me?</b></summary>

No, and that's deliberate. It has no login and only reads public data.
</details>

<details>
<summary><b>Is it official, safe and free?</b></summary>

It is unofficial and not affiliated with Milli.gold. It is read-only, runs on your machine and is free under the MIT license.
</details>

<details>
<summary><b>Do I need an Iranian IP or a proxy?</b></summary>

Not by default. If requests are blocked from your network, set `MILLIGOLD_MCP_PROXY` to an HTTP proxy. System proxy variables are ignored on purpose.
</details>

<details>
<summary><b>Claude Desktop says <code>uvx</code> is not found</b></summary>

Use the full path to `uvx` (`where uvx` on Windows, `which uvx` on macOS/Linux) as `command`.
</details>

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `MILLIGOLD_MCP_PROXY` | unset | Optional HTTP proxy URL for milli.gold requests. A comma-separated list is used one at a time: the next proxy takes over when one is blocked or cannot connect. System proxy settings are ignored |

<a id="فارسی"></a>

## فارسی: سرور MCP قیمت طلای میلی

<div dir="rtl">

**milligold-mcp** یک سرور MCP غیررسمی و فقط&zwnj;خواندنی برای [میلی (Milli.gold)](https://milli.gold)، پلتفرم آنلاین خرید و فروش طلای ۱۸ عیار آب&zwnj;شده به&zwnj;صورت میلی&zwnj;گرمی، است. این سرور به دستیار هوش مصنوعی شما (Claude، Cursor، Copilot و ...) اجازه می&zwnj;دهد قیمت لحظه&zwnj;ای طلا، تاریخچه قیمت، آمار پلتفرم، کارمزدها، هزینه معامله و اخبار و راهنمای میلی را بخواند.

**چه کارهایی می&zwnj;کند**

- **قیمت هر گرم طلای ۱۸ عیار** در میلی: ریال به ازای هر میلی&zwnj;گرم، ریال به ازای هر گرم و تومان به ازای هر گرم.
- **تاریخچه قیمت** روز، هفته و ماه گذشته، با اولین، آخرین، بیشترین و کمترین قیمت و درصد تغییر.
- **آمار پلتفرم**: تعداد کاربران، تعداد معاملات، طلای معامله&zwnj;شده و نگه&zwnj;داری&zwnj;شده (کیلوگرم)، طلای سوزانده&zwnj;شده و تعداد شعبه&zwnj;ها و نمایندگی&zwnj;ها.
- **کارمزدها**: کارمزد خرید، فروش، انتقال، تحویل طلا و برداشت از کیف پول، مستقیم از صفحه کارمزدهای سایت.
- **محاسبه هزینه معامله**: هزینه خرید چند گرم طلا (یا با یک بودجه تومانی) و مبلغ دریافتی از فروش، با کارمزد.
- **اخبار، مجله و راهنما**: تازه&zwnj;ترین مطالب (گزارش روزانه قیمت طلا و اونس)، جستجوی مقاله&zwnj;های راهنما و خواندن متن کامل هر مطلب.

**نکته&zwnj;ها**

- فقط خواندنی است: خرید و فروش نمی&zwnj;کند، وارد حساب نمی&zwnj;شود و به کیف پول دسترسی ندارد.
- قیمت، قیمت خود میلی است (بدون مالیات و اجرت)، نه قیمت بازار و نه قیمت tgju؛ برای نرخ دلار، سکه و ارز دیجیتال از [tgju-mcp](https://github.com/sepehr071/tgju-mcp) استفاده کنید.
- هر ۱ گرم برابر ۱۰۰۰ میلی&zwnj;گرم است؛ ۲۶۸٬۹۰۰ ریال به ازای هر میلی&zwnj;گرم یعنی ۲۶٬۸۹۰٬۰۰۰ تومان برای هر گرم.
- زمان&zwnj;ها به وقت تهران است. پاسخ&zwnj;ها ۱۵ ثانیه نگه داشته می&zwnj;شوند.
- روی سیستم خود شما اجرا می&zwnj;شود و کلید API لازم ندارد.

**نصب** (اول [uv](https://docs.astral.sh/uv/getting-started/installation/) را نصب کنید). در Claude Code:

</div>

```bash
claude mcp add milligold -- uvx milligold-mcp
```

<div dir="rtl">

در Claude Desktop، Cursor و بقیه برنامه&zwnj;ها همان تنظیم بخش [Quick start](#quick-start) را بگذارید.

**نمونه پرسش&zwnj;ها**

- «قیمت طلای ۱۸ عیار در میلی الان هر گرم چند تومان است؟»
- «قیمت طلا در میلی در یک ماه گذشته بیشترین و کمترین چقدر بوده؟»
- «امروز طلای آب&zwnj;شده در میلی گران&zwnj;تر شده یا ارزان&zwnj;تر؟»
- «آمار میلی را بگو: چند کاربر و چقدر طلا؟»

کلیدواژه&zwnj;ها: قیمت طلا، قیمت طلای ۱۸ عیار، خرید طلا آنلاین، طلای آب&zwnj;شده، قیمت هر گرم طلا، طلای دیجیتال، میلی.

</div>

## Development

```bash
git clone https://github.com/sepehr071/milligold-mcp && cd milligold-mcp
uv sync
uv run ruff check . && uv run ruff format --check .
uv run python -m pytest -q          # offline unit tests
uv run python -m pytest -m live -q  # calls milli.gold
uv build
```

Tools live in `src/milligold_mcp/gold.py`; each is a typed async function with a docstring that tells the agent when
to use it. Releases: bump the version in `pyproject.toml` and `server.json`, then push a `v*` tag.

## Related servers

- [tgju-mcp](https://github.com/sepehr071/tgju-mcp) for dollar, euro, gold, coin, crypto and commodity prices from tgju.org
- [iran-crypto-mcp](https://github.com/sepehr071/iran-crypto-mcp) for cryptocurrency prices on Iranian exchanges
- [tsetmc-mcp](https://github.com/sepehr071/tsetmc-mcp) for Tehran Stock Exchange data
- [iran-mcp](https://github.com/sepehr071/iran-mcp): catalog of all Iranian-service MCP servers
- Listed on [mcpfarsi.ir](https://mcpfarsi.ir/servers/milligold/), the Persian MCP marketplace

## Disclaimer

Unofficial and not affiliated with or endorsed by Milli.gold. It is read-only and uses public endpoints of milli.gold,
which can change without notice. Prices are informational and not financial advice.

## Author

<a href="https://www.linkedin.com/in/sepehr-radmard"><img src="https://raw.githubusercontent.com/sepehr071/iran-mcp/main/assets/author-banner.png" alt="Sepehr Radmard: open-source MCP servers for the Iranian web. LinkedIn: linkedin.com/in/sepehr-radmard" width="100%"></a>

Built and maintained by **Sepehr Radmard** (سپهر رادمرد). Connect on [LinkedIn](https://www.linkedin.com/in/sepehr-radmard) or follow [@sepehr071 on GitHub](https://github.com/sepehr071) for more MCP servers for Iranian websites, all listed in [iran-mcp](https://github.com/sepehr071/iran-mcp). If this saves you time, a star on the repo helps other people find it.

## License

[MIT](https://github.com/sepehr071/milligold-mcp/blob/main/LICENSE)
