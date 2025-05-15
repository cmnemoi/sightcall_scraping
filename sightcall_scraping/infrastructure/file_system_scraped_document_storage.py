import asyncio
import json
from pathlib import Path

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument
from sightcall_scraping.domain.ports.scraped_document_storage import ScrapedDocumentStorage


class FileSystemScrapedDocumentStorage(ScrapedDocumentStorage):
    def __init__(self, output_path: Path):
        self._output_path = output_path
        self._documents: list[ScrapedDocument] = []

    async def save_all(self, documents: list[ScrapedDocument]) -> None:
        self._documents.extend(documents)
        await asyncio.to_thread(self._write_to_file)

    def _write_to_file(self) -> None:
        with open(self._output_path, "w") as f:
            json.dump([self._to_dict(doc) for doc in self._documents], f, indent=4)

    @staticmethod
    def _to_dict(document: ScrapedDocument) -> dict:
        return {
            "url": document.url,
            "title": document.title,
            "content": document.content,
        }
