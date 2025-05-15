import asyncio
from typing import List, Tuple

import pytest

from sightcall_scraping.application.scrape_sightcall_website import ScrapeSightCallWebsite
from sightcall_scraping.domain.models.scraped_document import ScrapedDocument
from sightcall_scraping.domain.ports.scraped_document_storage import ScrapedDocumentStorage

EXPECTED_SCRAPED_DOCUMENT_COUNT: int = 2
EXPECTED_PROGRESS_BAR_TOTAL: int = 2
EXPECTED_BLOG_FETCH_COUNT: int = 4


def create_use_case(
    fake_content_fetcher, fake_document_parser, fake_scraped_document_storage, responses, rag_responses
) -> Tuple[ScrapeSightCallWebsite, ScrapedDocumentStorage]:
    content_fetcher = fake_content_fetcher(responses)
    document_parser = fake_document_parser(rag_responses)
    storage = fake_scraped_document_storage()
    return ScrapeSightCallWebsite(content_fetcher, document_parser, storage), storage


def expected_documents(rag_responses, html_responses) -> List[ScrapedDocument]:
    return [
        rag_responses[("https://sightcall.com/blog/", html_responses["https://sightcall.com/blog/"])],
        rag_responses[("https://sightcall.com/about", html_responses["https://sightcall.com/about"])],
    ]


@pytest.mark.asyncio
async def test_should_return_scraped_documents_for_all_urls_in_sitemap_index(
    fake_content_fetcher,
    fake_document_parser,
    fake_scraped_document_storage,
    sitemap_index_xml,
    post_sitemap_xml,
    page_sitemap_xml,
    html_responses,
    rag_responses,
):
    responses = {
        "https://sightcall.com/sitemap_index.xml": sitemap_index_xml,
        "https://sightcall.com/post-sitemap.xml": post_sitemap_xml,
        "https://sightcall.com/page-sitemap.xml": page_sitemap_xml,
        **html_responses,
    }
    use_case, _ = create_use_case(
        fake_content_fetcher, fake_document_parser, fake_scraped_document_storage, responses, rag_responses
    )
    documents = await use_case.execute("https://sightcall.com/sitemap_index.xml", lambda _: None)
    assert documents == expected_documents(rag_responses, html_responses)


@pytest.mark.asyncio
async def test_should_store_scraped_documents_for_all_urls_in_sitemap_index(
    fake_content_fetcher,
    fake_document_parser,
    fake_scraped_document_storage,
    sitemap_index_xml,
    post_sitemap_xml,
    page_sitemap_xml,
    html_responses,
    rag_responses,
):
    responses = {
        "https://sightcall.com/sitemap_index.xml": sitemap_index_xml,
        "https://sightcall.com/post-sitemap.xml": post_sitemap_xml,
        "https://sightcall.com/page-sitemap.xml": page_sitemap_xml,
        **html_responses,
    }
    use_case, storage = create_use_case(
        fake_content_fetcher, fake_document_parser, fake_scraped_document_storage, responses, rag_responses
    )
    documents = await use_case.execute("https://sightcall.com/sitemap_index.xml", lambda _: None)
    assert storage.saved_documents == expected_documents(rag_responses, html_responses)
    assert documents == expected_documents(rag_responses, html_responses)


@pytest.mark.asyncio
async def test_should_call_progress_callback_when_scraping_documents(
    fake_content_fetcher,
    fake_document_parser,
    fake_scraped_document_storage,
    sitemap_index_xml,
    post_sitemap_xml,
    page_sitemap_xml,
    html_responses,
    rag_responses,
):
    responses = {
        "https://sightcall.com/sitemap_index.xml": sitemap_index_xml,
        "https://sightcall.com/post-sitemap.xml": post_sitemap_xml,
        "https://sightcall.com/page-sitemap.xml": page_sitemap_xml,
        **html_responses,
    }
    use_case, _ = create_use_case(
        fake_content_fetcher, fake_document_parser, fake_scraped_document_storage, responses, rag_responses
    )
    progress_calls = []

    def on_progress(count):
        progress_calls.append(count)

    documents = await use_case.execute("https://sightcall.com/sitemap_index.xml", on_progress=on_progress)
    assert progress_calls == [1, 2]
    assert documents == expected_documents(rag_responses, html_responses)


@pytest.mark.asyncio
async def test_should_not_exceed_maximum_concurrent_requests_when_scraping_documents(
    fake_document_parser,
    fake_scraped_document_storage,
    sitemap_index_xml,
):
    # Given: 20 URLs to scrape and a fake fetcher that tracks concurrency
    sitemap_urls = [f"https://sightcall.com/sitemap-{i}.xml" for i in range(20)]
    page_urls = [f"https://sightcall.com/page/{i}" for i in range(20)]
    html_responses = {url: f"<html><title>Page {i}</title></html>" for i, url in enumerate(page_urls)}
    rag_responses = {
        (url, html_responses[url]): ScrapedDocument(url=url, title=f"Page {i}", content=f"Content {i}")
        for i, url in enumerate(page_urls)
    }
    responses = {
        "https://sightcall.com/sitemap_index.xml": sitemap_index_xml,
        **{sitemap_url: f"<xml>{sitemap_url}</xml>" for sitemap_url in sitemap_urls},
        **html_responses,
    }
    max_concurrent = 0
    current_concurrent = 0
    lock = asyncio.Lock()

    class FakeContentFetcher:
        async def fetch(self, url):
            nonlocal max_concurrent, current_concurrent
            # Only track concurrency for document fetches
            if url in html_responses:
                async with lock:
                    current_concurrent += 1
                    if current_concurrent > max_concurrent:
                        max_concurrent = current_concurrent
                    if current_concurrent > 10:
                        raise AssertionError(f"Exceeded max concurrency: {current_concurrent}")
                await asyncio.sleep(0.01)  # Simulate network delay
                async with lock:
                    current_concurrent -= 1
            return responses[url]

    # Patch the sitemap parser to return 20 sitemap URLs from the index, and one page URL per sitemap
    fake_parser = fake_document_parser(rag_responses)
    fake_storage = fake_scraped_document_storage()
    use_case = ScrapeSightCallWebsite(FakeContentFetcher(), fake_parser, fake_storage)

    def fake_parse(xml):
        if xml == sitemap_index_xml:
            return [type("Url", (), {"value": url})() for url in sitemap_urls]
        for i, sitemap_url in enumerate(sitemap_urls):
            if xml == f"<xml>{sitemap_url}</xml>":
                return [type("Url", (), {"value": page_urls[i]})()]
        return []

    use_case._sitemap_parser.parse = fake_parse

    # When: Executing the use case
    documents = await use_case.execute("https://sightcall.com/sitemap_index.xml", lambda _: None)

    # Then: All documents are scraped and concurrency never exceeds 10
    assert max_concurrent <= 10
    assert len(documents) == len(page_urls)
    assert fake_storage.saved_documents == list(rag_responses.values())


def test_should_call_on_progress_callback_for_each_scraped_document(
    fake_document_parser,
    fake_scraped_document_storage,
    sitemap_index_xml,
):
    # Given: 5 URLs to scrape
    sitemap_urls = [f"https://sightcall.com/sitemap-{i}.xml" for i in range(5)]
    page_urls = [f"https://sightcall.com/page/{i}" for i in range(5)]
    html_responses = {url: f"<html><title>Page {i}</title></html>" for i, url in enumerate(page_urls)}
    rag_responses = {
        (url, html_responses[url]): ScrapedDocument(url=url, title=f"Page {i}", content=f"Content {i}")
        for i, url in enumerate(page_urls)
    }
    responses = {
        "https://sightcall.com/sitemap_index.xml": sitemap_index_xml,
        **{sitemap_url: f"<xml>{sitemap_url}</xml>" for sitemap_url in sitemap_urls},
        **html_responses,
    }

    class FakeContentFetcher:
        async def fetch(self, url):
            return responses[url]

    fake_parser = fake_document_parser(rag_responses)
    fake_storage = fake_scraped_document_storage()
    use_case = ScrapeSightCallWebsite(FakeContentFetcher(), fake_parser, fake_storage)

    def fake_parse(xml):
        if xml == sitemap_index_xml:
            return [type("Url", (), {"value": url})() for url in sitemap_urls]
        for i, sitemap_url in enumerate(sitemap_urls):
            if xml == f"<xml>{sitemap_url}</xml>":
                return [type("Url", (), {"value": page_urls[i]})()]
        return []

    use_case._sitemap_parser.parse = fake_parse
    # Track progress callback calls
    progress_calls = []

    def on_progress(count):
        progress_calls.append(count)

    # When: Executing the use case with the progress callback
    import asyncio

    documents = asyncio.run(use_case.execute("https://sightcall.com/sitemap_index.xml", on_progress=on_progress))
    # Then: The callback is called once per document, in order
    assert progress_calls == [1, 2, 3, 4, 5]
    assert len(documents) == 5
    assert fake_storage.saved_documents == list(rag_responses.values())
