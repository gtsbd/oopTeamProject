
import csv

from repositories.base import LibraryRepository


class CSVRepository(LibraryRepository):

    def __init__(self, file_path: str):
        self._file_path = file_path

    def load(self) -> list[dict]:
        with open(
            self._file_path,
            mode="r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)
            return list(reader)
