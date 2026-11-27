
import random

from models.library import Library
from models.book import Book


class SimulationData:

    BOOK_TITLES = [
        "이기적 유전자",
        "사피엔스",
        "클린 코드",
        "코스모스",
        "총균쇠"
    ]

    def __init__(self, seed: int = 42):
        self._random = random.Random(seed)

    def apply(self, library: Library) -> None:
        titles = self._random.sample(
            self.BOOK_TITLES,
            self._random.randint(2, 4)
        )

        for title in titles:
            library.add_book(
                Book(title, "Dummy-ISBN")
            )

        max_seats = self._random.randint(50, 200)

        popularity = round(
            self._random.uniform(0.8, 1.2),
            2
        )

        library.set_capacity(
            max_seats,
            popularity
        )
