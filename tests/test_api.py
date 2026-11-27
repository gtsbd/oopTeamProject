
from unittest.mock import patch

import pytest

from repositories.seoul_api import SeoulAPIRepository


def test_load_multiple_pages():
    repository = SeoulAPIRepository(
        "test-key",
        page_size=2
    )

    pages = [
        ([{"id": 1}, {"id": 2}], 5),
        ([{"id": 3}, {"id": 4}], 5),
        ([{"id": 5}], 5)
    ]

    with patch.object(
        repository,
        "_request_page",
        side_effect=pages
    ) as request:

        rows = repository.load()

    assert len(rows) == 5
    assert request.call_count == 3
    assert rows[-1]["id"] == 5


def test_load_with_limit():
    repository = SeoulAPIRepository(
        "test-key",
        limit=3,
        page_size=2
    )

    pages = [
        ([{"id": 1}, {"id": 2}], 10),
        ([{"id": 3}], 10)
    ]

    with patch.object(
        repository,
        "_request_page",
        side_effect=pages
    ):
        rows = repository.load()

    assert len(rows) == 3


def test_empty_api_response():
    repository = SeoulAPIRepository("test-key")

    with patch.object(
        repository,
        "_request_page",
        return_value=([], 0)
    ):
        assert repository.load() == []


def test_invalid_page_size():
    with pytest.raises(ValueError):
        SeoulAPIRepository(
            "test-key",
            page_size=1001
        )


def test_incomplete_pagination():
    repository = SeoulAPIRepository(
        "test-key",
        page_size=2
    )

    with patch.object(
        repository,
        "_request_page",
        side_effect=[
            ([{"id": 1}, {"id": 2}], 5),
            ([], 0)
        ]
    ):
        with pytest.raises(RuntimeError):
            repository.load()
