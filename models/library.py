
from models.location import Location
from models.book import Book
from models.operating_hours import OperatingHours


class Library:

    def __init__(
        self,
        name: str,
        lat: float,
        lon: float,
        close_time=None,
        operating_hours=None,
        district="미확인",
        address=""
    ):
        self.name = name
        self.location = Location(lat, lon)
        self.district = district
        self.address = address

        if operating_hours is None:
            if close_time is not None:
                hours = (9 * 60, int(close_time * 60))

                operating_hours = OperatingHours(
                    weekday=hours,
                    weekend=hours
                )
            else:
                operating_hours = OperatingHours()

        self._operating_hours = operating_hours

        self.books = []
        self.max_seats = 0
        self.popularity = 1.0

    @property
    def operating_hours(self):
        return self._operating_hours

    @property
    def close_time(self):
        # 기존 코드와의 호환성을 위한 평일 마감시간
        return self._operating_hours.get_close_time("월")

    def get_close_time(self, day="월"):
        return self._operating_hours.get_close_time(day)

    def set_capacity(self, max_seats, popularity):
        self.max_seats = max_seats
        self.popularity = popularity

    def get_status(self, user_time, day="월"):
        return self._operating_hours.get_status(
            day, user_time
        )

    def is_open(self, user_time, day="월"):
        return self._operating_hours.is_open(
            day, user_time
        )

    def add_book(self, book: Book):
        self.books.append(book)

    def has_book(self, target_title):
        return any(
            book.title == target_title
            and book.check_available()
            for book in self.books
        )

    def get_congestion_rate(self, current_time, day="월"):
        if not self.is_open(current_time, day):
            return 0.0

        if current_time < 12:
            base_rate = 0.45
        elif current_time < 18:
            base_rate = 0.90
        elif current_time < 20:
            base_rate = 0.60
        else:
            base_rate = 0.75

        return min(
            base_rate * self.popularity * 100,
            100.0
        )

    def is_crowded(self, current_time, day="월"):
        return self.get_congestion_rate(
            current_time, day
        ) >= 85.0
