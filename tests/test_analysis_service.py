
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

def test_data_quality():
    result = AnalysisService().get_data_quality(
        sample_libraries()
    )

    assert result["total"] == 3
    assert result["complete_hours"] == 2
    assert result["incomplete_hours"] == 1


def test_weekly_statistics():
    result = AnalysisService().get_weekly_statistics(
        sample_libraries()
    )

    assert len(result) == 7 * 24


def test_user_comparison():
    results = AnalysisService().compare_user_types(
        sample_libraries(), "월"
    )

    assert len(results) == 24

    # 학생은 17시 방문
    # 직장인은 18시 방문
    assert results[17]["student"] == 2
    assert results[17]["worker"] == 1

    # 직장인은 24시 이후 방문하지 않음
    assert results[23]["worker"] == 0
