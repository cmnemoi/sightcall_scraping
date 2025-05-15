import json

import pytest

from sightcall_scraping.domain.models.scraped_document import ScrapedDocument
from sightcall_scraping.infrastructure.file_system_scraped_document_storage import FileSystemScrapedDocumentStorage


@pytest.mark.asyncio
async def test_should_save_documents_to_file(tmp_path):
    output_file = tmp_path / "scraped_documents.json"
    storage = FileSystemScrapedDocumentStorage(output_file)
    doc1 = ScrapedDocument(url="http://a", title="A", content="C")
    doc2 = ScrapedDocument(url="http://b", title="B", content="D")
    await storage.save_all([doc1, doc2])
    with open(output_file) as f:
        data = json.load(f)
    assert data == [
        {"url": "http://a", "title": "A", "content": "C"},
        {"url": "http://b", "title": "B", "content": "D"},
    ]
