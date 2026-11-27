
from models.library import Library
from repositories.base import LibraryRepository
from services.library_parser import LibraryParser
from services.simulation_data import SimulationData


class SystemManager:

    def __init__(self, repository: LibraryRepository):
        self._repository = repository
        self._parser = LibraryParser()

        self._libraries = []
        self._invalid_count = 0
        self._raw_count = 0

        self._load_data()

    def _load_data(self) -> None:
        rows = self._repository.load()

        self._raw_count = len(rows)
        simulation = SimulationData(seed=42)

        for row in rows:
            try:
                library = self._parser.parse(row)

            except (ValueError, TypeError, KeyError):
                self._invalid_count += 1
                continue

            simulation.apply(library)
            self._libraries.append(library)

    def get_libraries(self) -> list[Library]:
        return self._libraries.copy()

    @property
    def raw_count(self) -> int:
        return self._raw_count

    @property
    def invalid_count(self) -> int:
        return self._invalid_count
