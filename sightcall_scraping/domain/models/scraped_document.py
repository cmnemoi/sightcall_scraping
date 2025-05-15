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

    def __eq__(self, other):
        if not isinstance(other, ScrapedDocument):
            return False
        return self._url == other._url and self._title == other._title and self._content == other._content

    def __repr__(self):
        return f"ScrapedDocument(url={self._url!r}, title={self._title!r}, content=<...>)"
