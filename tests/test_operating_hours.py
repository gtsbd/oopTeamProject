
from models.operating_hours import OperatingHours


def sample_hours():
    return OperatingHours.from_text(
        "평일 : 09:00~22:00, 주말 : 09:00~17:00",
        "매주 화요일 및 법정공휴일"
    )


def test_weekday_open():
    assert sample_hours().is_open("월", 19)


def test_weekend_closed():
    assert not sample_hours().is_open("토", 19)


def test_regular_holiday():
    assert not sample_hours().is_open("화", 12)


def test_before_opening():
    assert not sample_hours().is_open("월", 8)


def test_exact_opening_time():
    assert sample_hours().is_open("월", 9)


def test_exact_closing_time():
    assert not sample_hours().is_open("월", 22)


def test_unknown_hours():
    hours = OperatingHours.from_text("미확인")

    assert hours.get_status("월", 12) == "unknown"


def test_minute_precision():
    hours = OperatingHours.from_text(
        "09:30~18:30"
    )

    assert not hours.is_open("월", 9)
    assert hours.is_open("월", 9.5)
    assert hours.is_open("월", 18.25)
    assert not hours.is_open("월", 18.5)
