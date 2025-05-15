from abc import ABC, abstractmethod


class ContentFetcher(ABC):
    @abstractmethod
    async def fetch(self, uri: str) -> str:
        pass
