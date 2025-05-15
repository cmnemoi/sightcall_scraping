import re

from bs4 import BeautifulSoup

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument
from sightcall_scraping.domain.ports.document_parser import DocumentParser


class HtmlDocumentParser(DocumentParser):
    def to_scraped_document(self, url: str, html: str) -> ScrapedDocument:
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        body = soup.body.get_text(separator=" ", strip=True) if soup.body else ""
        body = re.sub(r"\s+([!.,;:?])", r"\1", body)
        return ScrapedDocument(url=url, title=title, content=body)
