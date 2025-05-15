import httpx

from sightcall_scraping.domain.ports.content_fetcher import ContentFetcher

USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class HttpContentFetcher(ContentFetcher):
    async def fetch(self, uri: str) -> str:
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
            response = await client.get(uri)
            response.raise_for_status()
            return response.text
