import pytest

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument


@pytest.fixture(scope="function")
def fake_content_fetcher():
    class FakeContentFetcher:
        def __init__(self, responses):
            self._responses = responses

        async def fetch(self, uri: str) -> str:
            return self._responses[uri]

    return FakeContentFetcher


@pytest.fixture(scope="function")
def fake_document_parser():
    class FakeDocumentParser:
        def __init__(self, responses):
            self._responses = responses

        def to_scraped_document(self, url: str, html: str):
            return self._responses[(url, html)]

    return FakeDocumentParser


@pytest.fixture(scope="function")
def fake_scraped_document_storage():
    class FakeScrapedDocumentStorage:
        def __init__(self):
            self.saved_documents: list[ScrapedDocument] = []

        async def save_all(self, documents: list[ScrapedDocument]) -> None:
            self.saved_documents.extend(documents)

    return FakeScrapedDocumentStorage


@pytest.fixture(scope="function")
def sitemap_index_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n  <sitemap>\n    <loc>https://sightcall.com/post-sitemap.xml</loc>\n  </sitemap>\n  <sitemap>\n    <loc>https://sightcall.com/page-sitemap.xml</loc>\n  </sitemap>\n</sitemapindex>\n"""


@pytest.fixture(scope="function")
def post_sitemap_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n  <url>\n    <loc>https://sightcall.com/blog/</loc>\n  </url>\n</urlset>\n"""


@pytest.fixture(scope="function")
def page_sitemap_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n  <url>\n    <loc>https://sightcall.com/about</loc>\n  </url>\n</urlset>\n"""


@pytest.fixture
def sitemap_xml() -> str:
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:image=\"http://www.google.com/schemas/sitemap-image/1.1\" xsi:schemaLocation=\"http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd http://www.google.com/schemas/sitemap-image/1.1 http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd\" xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n\t<url>\n\t\t<loc>https://sightcall.com/blog/</loc>\n\t\t<lastmod>2025-05-14T21:48:38+00:00</lastmod>\n\t</url>\n\t<url>\n\t\t<loc>https://sightcall.com/blog/telecom-embrace-api-fication-trend-new-revenue/</loc>\n\t\t<lastmod>2024-07-09T16:36:57+00:00</lastmod>\n\t\t<image:image>\n\t\t\t<image:loc>https://sightcall.com/wp-content/uploads/sightcall_bg-3.jpg</image:loc>\n\t\t</image:image>\n\t</url>\n</urlset>\n"""


@pytest.fixture(scope="function")
def html_responses() -> dict[str, str]:
    return {
        "https://sightcall.com/blog/": "<html><head><title>Blog</title></head><body>Blog Content</body></html>",
        "https://sightcall.com/about": "<html><head><title>About</title></head><body>About Content</body></html>",
    }


@pytest.fixture(scope="function")
def rag_responses(html_responses: dict[str, str]) -> dict[tuple[str, str], ScrapedDocument]:
    return {
        ("https://sightcall.com/blog/", html_responses["https://sightcall.com/blog/"]): ScrapedDocument(
            url="https://sightcall.com/blog/", title="Blog", content="Blog Content"
        ),
        ("https://sightcall.com/about", html_responses["https://sightcall.com/about"]): ScrapedDocument(
            url="https://sightcall.com/about", title="About", content="About Content"
        ),
    }
