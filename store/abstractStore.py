from abc import ABC, abstractmethod


class AbstractStore(ABC):
    @abstractmethod
    async def get_books(self, search_query: str):
        pass
