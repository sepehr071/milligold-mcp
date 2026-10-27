import httpx
import pytest
from conftest import page

pytestmark = pytest.mark.anyio


async def test_latest_posts_from_feed(client, api):
    api["/news/feed/"] = page("news_feed.xml")
    r = (await client.call_tool("mg_latest_posts", {"limit": 2})).structured_content
    assert len(r["posts"]) == 2
    post = r["posts"][1]
    assert post["date"] == "2026-10-27 10:45"  # 07:15 UTC in Tehran time
    assert post["url"].startswith("https://milli.gold/news/قیمت-طلا")
    assert "۲۶ میلیون" in post["summary"] and "نوشته" not in post["summary"]
    assert post["categories"] == ["اخبار روز", "قیمت طلا"]


async def test_help_topics_match_english_keywords(client, api):
    api["/help/post-sitemap.xml"] = page("help_sitemap.xml")
    r = (await client.call_tool("mg_help_topics", {"query": "Delivery physical"})).structured_content
    assert r["count"] >= 1 and all("delivery" in t["topic"] for t in r["topics"])
    assert (await client.call_tool("mg_help_topics", {})).structured_content["count"] > 50


async def test_read_extracts_article_text(client, api):
    api["/news/test-post/"] = page("news_article.html")
    r = (await client.call_tool("mg_read", {"url": "https://milli.gold/news/test-post/"})).structured_content
    assert r["title"].startswith("قیمت طلا امروز")
    assert "۲۶ میلیون و ۳۵۸ هزار" in r["text"] and "اونس جهانی طلا | ۴ هزار و ۳ دلار" in r["text"]
    assert "گوگل" not in r["text"] and "site footer" not in r["text"] and r["truncated"] is False
    r = (
        await client.call_tool("mg_read", {"url": "https://milli.gold/news/test-post/", "max_chars": 500})
    ).structured_content
    assert len(r["text"]) == 500 and r["truncated"] is True


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/news/x/",
        "http://milli.gold/news/x/",
        "https://milli.gold/",
        "https://milli.gold/main/terms/",
    ],
)
async def test_read_refuses_other_urls(client, api, url):
    r = await client.call_tool("mg_read", {"url": url})
    assert r.is_error and "milli.gold/news/" in r.content[0].text
    assert not api.calls


async def test_read_page_without_body_is_error(client, api):
    api["/help/x/"] = lambda r: httpx.Response(200, text="<html><body>nothing</body></html>")
    r = await client.call_tool("mg_read", {"url": "https://milli.gold/help/x/"})
    assert r.is_error and "no article" in r.content[0].text
