import asyncio
import logging
from typing import Awaitable, Callable, List, Optional, TypeVar

from tqdm import tqdm

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument
from sightcall_scraping.domain.models.url import Url
from sightcall_scraping.domain.ports.content_fetcher import ContentFetcher
from sightcall_scraping.domain.ports.document_parser import DocumentParser
from sightcall_scraping.domain.ports.scraped_document_storage import ScrapedDocumentStorage
from sightcall_scraping.domain.sitemap_parser import SitemapParser

T = TypeVar("T")

MAX_RETRY_ATTEMPTS: int = 3
INITIAL_BACKOFF_DELAY_SECONDS: float = 1.0
BACKOFF_MULTIPLIER: float = 3.0
SITEMAP_PROGRESS_DESCRIPTION: str = "Parsing sitemaps"
DOCUMENT_PROGRESS_DESCRIPTION: str = "Scraping documents"
MAX_CONCURRENT_REQUESTS: int = 10


class ScrapeSightCallWebsite:
    def __init__(
        self, content_fetcher: ContentFetcher, document_parser: DocumentParser, storage: ScrapedDocumentStorage
    ):
        self._content_fetcher = content_fetcher
        self._document_parser = document_parser
        self._storage = storage
        self._sitemap_parser = SitemapParser()

    async def execute(
        self,
        sitemap_index_url: str,
        on_progress: Callable[[int], None],
        max_urls: Optional[int] = None,
    ) -> List[ScrapedDocument]:
        sitemap_urls: List[Url] = await self._fetch_all_urls_from_sitemap_index(sitemap_index_url, max_urls)
        scraped_documents: List[ScrapedDocument] = await self._scrape_documents_from_urls(
            [url.value for url in sitemap_urls], on_progress
        )
        await self._storage.save_all(scraped_documents)
        return scraped_documents

    async def _fetch_all_urls_from_sitemap_index(self, sitemap_index_url: str, max_urls: Optional[int]) -> List[Url]:
        sitemap_index_xml: str = await self._content_fetcher.fetch(sitemap_index_url)
        sitemap_url_objects: List[Url] = self._sitemap_parser.parse(sitemap_index_xml)
        return await self._collect_urls_from_sitemaps(sitemap_url_objects, max_urls)

    async def _collect_urls_from_sitemaps(self, sitemap_url_objects: List[Url], max_urls: Optional[int]) -> List[Url]:
        collected_urls: List[Url] = []
        for sitemap_url_object in tqdm(
            sitemap_url_objects, total=len(sitemap_url_objects), desc=SITEMAP_PROGRESS_DESCRIPTION
        ):
            if self._is_max_urls_reached(collected_urls, max_urls):
                break
            sitemap_xml: Optional[str] = await self._fetch_sitemap_with_retry(sitemap_url_object.value)
            if sitemap_xml is None:
                continue
            urls_in_sitemap: List[Url] = self._sitemap_parser.parse(sitemap_xml)
            for url in urls_in_sitemap:
                if self._is_max_urls_reached(collected_urls, max_urls):
                    break
                collected_urls.append(url)
        return collected_urls

    async def _fetch_sitemap_with_retry(self, sitemap_url: str) -> Optional[str]:
        async def fetch() -> str:
            return await self._content_fetcher.fetch(sitemap_url)

        return await self._run_with_retry(
            fetch, MAX_RETRY_ATTEMPTS, sitemap_url, "[SITEMAP_FAIL] Skipping sitemap after retries"
        )

    async def _scrape_documents_from_urls(
        self, urls: List[str], on_progress: Callable[[int], None]
    ) -> List[ScrapedDocument]:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        progress_count = 0
        documents: List[ScrapedDocument] = []

        async def fetch_and_parse_with_semaphore(url: str) -> Optional[ScrapedDocument]:
            async with semaphore:
                return await self._fetch_and_parse_with_retry(url)

        async def fetch_and_report_progress(url: str) -> Optional[ScrapedDocument]:
            nonlocal progress_count
            document = await fetch_and_parse_with_semaphore(url)
            progress_count += 1
            on_progress(progress_count)
            return document

        coroutines = [fetch_and_report_progress(url) for url in urls]
        for document in await asyncio.gather(*coroutines):
            if document is not None:
                documents.append(document)
        return documents

    async def _fetch_and_parse_with_retry(self, url: str) -> Optional[ScrapedDocument]:
        async def fetch_and_parse() -> ScrapedDocument:
            html: str = await self._content_fetcher.fetch(url)
            return self._document_parser.to_scraped_document(url, html)

        return await self._run_with_retry(
            fetch_and_parse, MAX_RETRY_ATTEMPTS, url, "[SCRAPE_FAIL] Skipping URL after retries"
        )

    async def _run_with_retry(
        self,
        func: Callable[[], Awaitable[T]],
        max_attempts: int,
        url: Optional[str],
        fail_message: str,
        initial_delay: float = INITIAL_BACKOFF_DELAY_SECONDS,
        backoff_factor: float = BACKOFF_MULTIPLIER,
    ) -> Optional[T]:
        attempt: int = 0
        delay: float = initial_delay
        while attempt < max_attempts:
            try:
                return await func()
            except Exception as error:
                attempt += 1
                is_last_attempt: bool = attempt == max_attempts
                if is_last_attempt:
                    logging.warning(f"{fail_message}: {url} ({error})")
                    return None
                logging.info(
                    f"[RETRY] Attempt {attempt} failed for {url or ''}: {error}. Retrying in {delay} seconds..."
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
        return None

    def _noop_progress(self, _: int) -> None:
        pass

    def _is_max_urls_reached(self, collected_urls: List[Url], max_urls: Optional[int]) -> bool:
        return max_urls is not None and len(collected_urls) >= max_urls
