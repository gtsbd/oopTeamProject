
import re
import math

from models.operating_hours import OperatingHours
from models.library import Library


class LibraryParser:

    @staticmethod
    
    @staticmethod
    def parse_close_time(time_str: str) -> int:
        # 평일 운영시간 우선 추출
        weekday = re.search(
            r"평일\s*:\s*"
            r"(\d{1,2}):(\d{2})\s*[~～-]\s*"
            r"(\d{1,2}):(\d{2})",
            str(time_str)
        )

        # 기존 단순 시간 형식도 지원
        simple = re.fullmatch(
            r"\s*(\d{1,2}):(\d{2})\s*[~～-]\s*"
            r"(\d{1,2}):(\d{2})\s*",
            str(time_str)
        )

        match = weekday or simple

        if not match:
            raise ValueError("운영시간 형식 오류")

        start, start_min, end, end_min = map(
            int, match.groups()
        )

        if not (
            0 <= start < 24
            and 0 <= start_min < 60
            and 0 <= end <= 24
            and 0 <= end_min < 60
        ):
            raise ValueError("잘못된 운영시간")

        if end == 24 and end_min != 0:
            raise ValueError("잘못된 마감시간")

        if start * 60 + start_min >= end * 60 + end_min:
            raise ValueError("지원하지 않는 운영시간 범위")

        return end


    @staticmethod
    def parse_coordinates(row: dict) -> tuple:
        x = float(row["XCNTS"])
        y = float(row["YDNTS"])

        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("잘못된 좌표")

        # 서울 지역 좌표 범위를 이용한 순서 확인
        if 37 <= x <= 38 and 126 <= y <= 128:
            return x, y

        if 37 <= y <= 38 and 126 <= x <= 128:
            return y, x

        raise ValueError("서울 지역 좌표 범위 오류")

    
    def parse(self, row: dict) -> Library:
        name = str(
            row.get("LBRRY_NAME") or ""
        ).strip()

        if not name:
            raise ValueError("도서관 이름 누락")

        lat, lon = self.parse_coordinates(row)

        operating_hours = OperatingHours.from_text(
            row.get("OP_TIME", ""),
            row.get("FDRM_CLOSE_DATE", "")
        )

        district = str(
            row.get("CODE_VALUE") or "미확인"
        ).strip()

        address = str(
            row.get("ADRES") or ""
        ).strip()

        return Library(
            name=name,
            lat=lat,
            lon=lon,
            operating_hours=operating_hours,
            district=district,
            address=address
        )

