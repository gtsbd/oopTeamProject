
from models.library import Library
from models.operating_hours import OperatingHours
from services.analysis_service import AnalysisService


def sample_libraries():
    return [
        Library(
            "A", 37.5, 127.0,
            operating_hours=OperatingHours.from_text(
                "09:00~22:00"
            ),
            district="강남구"
        ),
        Library(
            "B", 37.6, 127.0,
            operating_hours=OperatingHours.from_text(
                "09:00~18:00"
            ),
            district="노원구"
        ),
        Library(
            "C", 37.6, 127.1,
            operating_hours=OperatingHours(),
            district="노원구"
        )
    ]


def test_status_summary():
    service = AnalysisService()

    result = service.get_summary(
        sample_libraries(), "월", 19
    )

    assert result["total"] == 3
    assert result["open"] == 1
    assert result["closed"] == 1
    assert result["unknown"] == 1
    assert result["open_rate"] == 50.0


def test_hourly_statistics():
    service = AnalysisService()

    results = service.get_hourly_statistics(
        sample_libraries(), "월"
    )

    assert len(results) == 24
    assert results[19]["open"] == 1


def test_district_statistics():
    service = AnalysisService()

    results = service.get_district_statistics(
        sample_libraries(), "월", 19
    )

    assert len(results) == 2
    assert sum(row["total"] for row in results) == 3


def test_empty_libraries():
    result = AnalysisService().get_summary(
        [], "월", 19
    )

    assert result["total"] == 0
    assert result["open_rate"] is None
