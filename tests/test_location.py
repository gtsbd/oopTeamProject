
import pytest

from models.location import Location


def test_same_location():
    a = Location(37.5, 127.0)
    b = Location(37.5, 127.0)

    assert a.calculate_distance(b) == 0


def test_distance_symmetry():
    a = Location(37.5, 127.0)
    b = Location(37.6, 127.1)

    assert a.calculate_distance(b) == pytest.approx(
        b.calculate_distance(a)
    )


def test_known_distance():
    a = Location(0, 0)
    b = Location(1, 0)

    assert a.calculate_distance(b) == pytest.approx(
        111.195, abs=0.01
    )


def test_invalid_latitude():
    with pytest.raises(ValueError):
        Location(100, 127.0)


def test_invalid_longitude():
    with pytest.raises(ValueError):
        Location(37.5, 200)
