class ScrapedDocument:
    def __init__(self, url: str, title: str, content: str):
        self._url = url
        self._title = title
        self._content = content

    @property
    def url(self) -> str:
        return self._url

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content
