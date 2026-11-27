
from abc import ABC, abstractmethod


class LibraryRepository(ABC):

    @abstractmethod
    def load(self) -> list[dict]:
        pass
