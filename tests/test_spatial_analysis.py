
import pytest

from models.location import Location
from models.library import Library
from models.operating_hours import OperatingHours

from services.spatial_analysis_service import (
    SpatialAnalysisService
)


def sample_libraries():
    return [
        Library(
            "가까운 도서관",
            37.505, 127.0,
            close_time=22
        ),
        Library(
            "중간 도서관",
            37.52, 127.0,
            close_time=18
        ),
        Library(
            "먼 도서관",
            37.60, 127.0,
            close_time=22
        )
    ]


def test_radius_filter():
    service = SpatialAnalysisService()
    origin = Location(37.5, 127.0)

    result = service.get_nearby_libraries(
        sample_libraries(),
        origin,
        1
    )

    assert len(result) == 1

    assert result[0]["library"].name == (
        "가까운 도서관"
    )


def test_radius_statistics():
    service = SpatialAnalysisService()
    origin = Location(37.5, 127.0)

    result = service.get_radius_statistics(
        sample_libraries(),
        origin,
        "월",
        19,
        radii=(1, 3)
    )

    assert result[0]["total"] == 1
    assert result[0]["open"] == 1

    assert result[1]["total"] == 2
    assert result[1]["open"] == 1
    assert result[1]["closed"] == 1


def test_unknown_status():
    library = Library(
        "미확인 도서관",
        37.5, 127.0,
        operating_hours=OperatingHours()
    )

    result = SpatialAnalysisService().get_radius_statistics(
        [library],
        Location(37.5, 127.0),
        "월",
        12,
        radii=(1,)
    )

    assert result[0]["unknown"] == 1
    assert result[0]["open_rate"] is None


def test_invalid_radius():
    with pytest.raises(ValueError):
        SpatialAnalysisService().get_nearby_libraries(
            [],
            Location(37.5, 127.0),
            0
        )


def test_empty_libraries():
    result = SpatialAnalysisService().get_nearby_libraries(
        [],
        Location(37.5, 127.0),
        3
    )

    assert result == []
