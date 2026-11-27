
import re


class OperatingHours:

    DAYS = (
        "월", "화", "수", "목", "금", "토", "일"
    )

    TIME_PATTERN = (
        r"(\d{1,2}):(\d{2})\s*[~～\-–]\s*"
        r"(\d{1,2}):(\d{2})"
    )

    def __init__(
        self,
        weekday=None,
        weekend=None,
        closed_days=None,
        raw_close=""
    ):
        self._weekday = weekday
        self._weekend = weekend
        self._closed_days = frozenset(closed_days or [])
        self._raw_close = raw_close

    @property
    def weekday(self):
        return self._weekday

    @property
    def weekend(self):
        return self._weekend

    @property
    def closed_days(self):
        return self._closed_days

    @property
    def raw_close(self):
        return self._raw_close

    @classmethod
    def _parse_range(cls, text):
        match = re.fullmatch(
            cls.TIME_PATTERN,
            text.strip()
        )

        if not match:
            return None

        sh, sm, eh, em = map(
            int, match.groups()
        )

        if not (
            0 <= sh < 24
            and 0 <= sm < 60
            and 0 <= eh <= 24
            and 0 <= em < 60
        ):
            return None

        if eh == 24 and em != 0:
            return None

        start = sh * 60 + sm
        end = eh * 60 + em

        if start >= end:
            return None

        return start, end

    @classmethod
    def from_text(cls, hours_text, close_text=""):
        hours_text = str(hours_text or "")
        close_text = str(close_text or "")

        weekday = None
        weekend = None

        for part in re.split(r"[,;.\n]", hours_text):
            part = part.strip()

            for label in ("평일", "주말"):
                match = re.fullmatch(
                    rf"{label}\s*[:：]?\s*(.+)",
                    part
                )

                if match:
                    hours = cls._parse_range(
                        match.group(1)
                    )

                    if label == "평일":
                        weekday = hours
                    else:
                        weekend = hours

        # 단순 운영시간은 평일·주말 공통으로 가정
        simple = cls._parse_range(hours_text)

        if simple is not None:
            weekday = simple
            weekend = simple

        # 매주 지정된 휴관 요일 추출
        closed_days = re.findall(
            r"매주\s*([월화수목금토일])요일",
            close_text
        )

        return cls(
            weekday,
            weekend,
            closed_days,
            close_text
        )

    def get_status(self, day, time):
        if day not in self.DAYS:
            raise ValueError("잘못된 요일입니다.")

        if not 0 <= time <= 24:
            raise ValueError("잘못된 시간입니다.")

        if day in self._closed_days:
            return "closed"

        if time == 24:
            return "closed"

        hours = (
            self._weekend
            if day in ("토", "일")
            else self._weekday
        )

        if hours is None:
            return "unknown"

        current = time * 60
        start, end = hours

        if start <= current < end:
            return "open"

        return "closed"

    def is_open(self, day, time):
        return self.get_status(day, time) == "open"

    def get_close_time(self, day):
        hours = (
            self._weekend
            if day in ("토", "일")
            else self._weekday
        )

        if hours is None:
            return None

        return hours[1] / 60
