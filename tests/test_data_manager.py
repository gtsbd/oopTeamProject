
import pytest

from data_manager import SystemManager
from repositories.base import LibraryRepository
from repositories.csv_repository import CSVRepository
from services.library_parser import LibraryParser


class FakeRepository(LibraryRepository):

    def __init__(self, rows):
        self._rows = rows

    def load(self):
        return self._rows


def valid_row():
    return {
        "LBRRY_NAME": "테스트 도서관",
        "XCNTS": "37.5",
        "YDNTS": "127.0",
        "OP_TIME": "09:00~22:00"
    }


def test_valid_data():
    manager = SystemManager(
        FakeRepository([valid_row()])
    )

    assert len(manager.get_libraries()) == 1
    assert manager.raw_count == 1
    assert manager.invalid_count == 0


def test_invalid_data():
    invalid = valid_row()
    invalid["XCNTS"] = "invalid"

    manager = SystemManager(
        FakeRepository([invalid, valid_row()])
    )

    assert len(manager.get_libraries()) == 1
    assert manager.raw_count == 2
    assert manager.invalid_count == 1


def test_empty_data():
    manager = SystemManager(FakeRepository([]))

    assert manager.get_libraries() == []
    assert manager.raw_count == 0


def test_close_time():
    assert LibraryParser.parse_close_time(
        "09:00~22:00"
    ) == 22


def test_invalid_time():
    with pytest.raises(ValueError):
        LibraryParser.parse_close_time("운영시간 미상")


def test_coordinate_order():
    row = valid_row()
    row["XCNTS"] = "127.0"
    row["YDNTS"] = "37.5"

    assert LibraryParser.parse_coordinates(row) == (
        37.5, 127.0
    )


def test_reproducible_simulation():
    a = SystemManager(FakeRepository([valid_row()]))
    b = SystemManager(FakeRepository([valid_row()]))

    lib_a = a.get_libraries()[0]
    lib_b = b.get_libraries()[0]

    assert lib_a.max_seats == lib_b.max_seats
    assert lib_a.popularity == lib_b.popularity

    assert [book.title for book in lib_a.books] == [
        book.title for book in lib_b.books
    ]


def test_csv_repository(tmp_path):
    path = tmp_path / "libraries.csv"

    path.write_text(
        "LBRRY_NAME,XCNTS,YDNTS,OP_TIME\n"
        "테스트 도서관,37.5,127.0,09:00~22:00\n",
        encoding="utf-8"
    )

    manager = SystemManager(
        CSVRepository(str(path))
    )

    assert len(manager.get_libraries()) == 1

@pytest.mark.parametrize(
    "time_str, expected",
    [
        ("평일 : 09:00~22:00, 주말 : 09:00~22:00", 22),
        ("평일 : 09:00~18:00, 주말 : 09:00~17:00", 18),
        ("평일 : 09:00~22:00, 주말 : 09:00~17:00", 22),
        ("09:00~18:00", 18),
    ]
)
def test_real_api_time_format(time_str, expected):
    assert LibraryParser.parse_close_time(
        time_str
    ) == expected
