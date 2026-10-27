"""Milli.gold content tools: latest news, magazine and help posts, help topic search, article reader."""

from __future__ import annotations

import html
import re
from email.utils import parsedate_to_datetime
from typing import Annotated, Any, Literal
from urllib.parse import unquote

import httpx
from pydantic import Field

from .gold import TEHRAN
from .http import SITE, ApiError, fetch
from .registry import tool

SECTIONS = ("news", "mag", "help")
# Cut-off markers after an article body (news/mag theme, then the help center's Elementor layout).
BODY_START = ('class="entry-content', 'data-widget_type="theme-post-content.default"', "<article", "<main")
BODY_END = ('class="post-bottom-meta', 'id="share-buttons', "</article>", "<footer", 'class="elementor-location-footer')
NOISE = {"میلی را در گوگل بیشتر ببینید"}  # "follow Milli on Google" button


def _text(fragment: str) -> list[str]:
    """Visible text of an HTML fragment, one block per line; table cells joined with ' | '."""
    s = re.sub(r"<(script|style|svg|nav|aside|form|noscript)\b.*?</\1>", "", fragment, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</(p|h[1-6]|li|tr|div|section|blockquote)>", "\n", s, flags=re.I)
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return [x for x in (line.strip().strip("|").strip() for line in s.splitlines()) if len(x) > 1 and x not in NOISE]


def _tag(item: str, name: str) -> str:
    m = re.search(rf"<{name}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{name}>", item, re.S)
    return m[1].strip() if m else ""


@tool("Milli.gold latest posts")
async def mg_latest_posts(
    section: Annotated[
        Literal["news", "mag", "help"],
        Field(
            description="news = daily gold price and market news, mag = gold buying guides, help = how to use Milli."
        ),
    ] = "news",
    limit: Annotated[int, Field(description="How many posts to return, newest first (1-20).", ge=1, le=20)] = 10,
) -> dict[str, Any]:
    """List the newest posts on Milli.gold's news, magazine or help site, with date, categories, summary and URL.

    News carries daily 18k gold, ounce, coin and market reports in Persian. Only the newest posts are available
    (about 20 news, 10 mag, 10 help); there is no search or older pages. Read a full post with mg_read.
    """
    feed = await fetch(f"{SITE}/{section}/feed/", text=True)
    items = re.findall(r"<item>(.*?)</item>", feed, re.S)
    if not items:
        raise ApiError(f"Milli.gold returned no {section} feed.")
    posts = []
    for it in items[:limit]:
        try:
            date = parsedate_to_datetime(_tag(it, "pubDate")).astimezone(TEHRAN).strftime("%Y-%m-%d %H:%M")
        except (TypeError, ValueError):
            date = None
        summary = _text(
            re.split(r"<p>\s*نوشته\s", _tag(it, "description"))[0]
        )  # drop the feed's "first published on" footer
        posts.append(
            {
                "title": html.unescape(_tag(it, "title")),
                "date": date,
                "categories": re.findall(r"<category><!\[CDATA\[(.*?)\]\]></category>", it),
                "summary": " ".join(summary)[:400],
                "url": unquote(_tag(it, "link")),
            }
        )
    return {"section": section, "posts": posts}


@tool("Milli.gold help topics")
async def mg_help_topics(
    query: Annotated[
        str,
        Field(
            description="English keywords matched against help article URLs, e.g. 'delivery', 'fee', 'card'. Empty = all."
        ),
    ] = "",
) -> dict[str, Any]:
    """Find Milli.gold help-center articles (how to buy, sell, deliver, transfer, verify, fees) by English keyword.

    The help center has about 80 articles in Persian; their URLs are English, so match on English words. Read an
    article with mg_read. For the fee table itself use mg_fees.
    """
    sitemap = await fetch(f"{SITE}/help/post-sitemap.xml", text=True)
    urls = re.findall(r"<loc>(https://milli\.gold/help/[^<]+)</loc>", sitemap)
    if not urls:
        raise ApiError("Milli.gold returned no help sitemap.")
    words = query.lower().split()
    topics = []
    for url in urls:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        topic = " ".join(w for w in slug.split("-") if not w.isdigit())
        if all(w in topic for w in words):
            topics.append({"topic": topic, "url": url})
    return {"query": query, "count": len(topics), "topics": topics}


@tool("Milli.gold read post")
async def mg_read(
    url: Annotated[
        str, Field(description="URL of a milli.gold news, mag or help post, from mg_latest_posts or mg_help_topics.")
    ],
    max_chars: Annotated[
        int, Field(description="Cut the text at this many characters (500-20000).", ge=500, le=20000)
    ] = 6000,
) -> dict[str, Any]:
    """Read the text of one Milli.gold news, magazine or help post, with tables flattened to 'a | b | c' lines.

    Only milli.gold news, mag and help URLs are accepted. Text is Persian; digits stay as written on the page.
    """
    u = httpx.URL(url.strip())
    parts = u.path.strip("/").split("/")
    if u.scheme != "https" or u.host != "milli.gold" or len(parts) < 2 or parts[0] not in SECTIONS:
        raise ApiError("Give a https://milli.gold/news/, /mag/ or /help/ post URL.")
    page = await fetch(str(u), text=True)
    title = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    start = next((i for m in BODY_START if (i := page.find(m)) >= 0), -1)
    if start < 0:
        raise ApiError("Milli.gold page has no article body.")
    body = page[page.find(">", start) + 1 :]
    end = min((j for m in BODY_END if (j := body.find(m)) > 0), default=len(body))
    lines = _text(body[:end])
    if not lines:
        raise ApiError("Milli.gold page has no article text.")
    text = "\n".join(lines)
    return {
        "title": " ".join(_text(title[1])) if title else None,
        "url": unquote(str(u)),
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }
