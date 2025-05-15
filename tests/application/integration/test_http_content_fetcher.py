import pytest

from sightcall_scraping.infrastructure.http_content_fetcher import HttpContentFetcher


@pytest.mark.asyncio
async def test_http_content_fetcher_fetches_html():
    fetcher = HttpContentFetcher()
    html = await fetcher.fetch("https://example.com/")
    assert "<title>Example Domain</title>" in html
