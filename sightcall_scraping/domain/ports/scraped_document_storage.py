from abc import ABC, abstractmethod

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument


class ScrapedDocumentStorage(ABC):
    @abstractmethod
    async def save_all(self, documents: list[ScrapedDocument]) -> None:
        pass
