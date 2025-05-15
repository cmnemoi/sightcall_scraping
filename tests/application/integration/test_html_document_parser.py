from sightcall_scraping.infrastructure.html_document_parser import HtmlDocumentParser


def test_html_document_parser_extracts_rag_fields():
    html = """
    <html>
      <head><title>Test Page</title></head>
      <body>
        <div>Hello <b>World</b>!</div>
      </body>
    </html>
    """
    parser = HtmlDocumentParser()
    doc = parser.to_scraped_document("https://test.com", html)
    assert doc.url == "https://test.com"
    assert doc.title == "Test Page"
    assert doc.content == "Hello World!"
