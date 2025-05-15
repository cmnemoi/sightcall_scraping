from abc import ABC, abstractmethod

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument


class DocumentParser(ABC):
    @abstractmethod
    def to_scraped_document(self, url: str, raw: str) -> ScrapedDocument:
        pass
