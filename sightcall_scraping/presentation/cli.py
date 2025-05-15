import asyncio
from pathlib import Path
from typing import Optional

import rich
import typer

from sightcall_scraping.application.scrape_sightcall_website import ScrapeSightCallWebsite
from sightcall_scraping.infrastructure.file_system_scraped_document_storage import FileSystemScrapedDocumentStorage
from sightcall_scraping.infrastructure.html_document_parser import HtmlDocumentParser
from sightcall_scraping.infrastructure.http_content_fetcher import HttpContentFetcher

app = typer.Typer()

SIGHTCALL_SITEMAP_INDEX_URL = "https://sightcall.com/sitemap_index.xml"
DEFAULT_OUTPUT_FILE = "data.json"


@app.command()
def scrape(
    max_urls: Optional[int] = typer.Option(None, help="Maximum number of URLs to scrape."),
    output_file: Path = typer.Option(DEFAULT_OUTPUT_FILE, help="File to write scraped documents to."),
) -> None:
    scrape_website_use_case = ScrapeSightCallWebsite(
        content_fetcher=HttpContentFetcher(),
        document_parser=HtmlDocumentParser(),
        storage=FileSystemScrapedDocumentStorage(output_file),
    )

    def on_progress(document_count: int) -> None:
        rich.print(f"Scraped {document_count} documents so far...")

    scraped_documents = asyncio.run(
        scrape_website_use_case.execute(
            SIGHTCALL_SITEMAP_INDEX_URL,
            on_progress,
            max_urls=max_urls,
        )
    )
    rich.print(f"Scraped {len(scraped_documents)} documents to {output_file} successfully!")


if __name__ == "__main__":
    app()
