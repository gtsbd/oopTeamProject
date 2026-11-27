
import requests

from repositories.base import LibraryRepository


class SeoulAPIRepository(LibraryRepository):

    def __init__(
        self,
        api_key: str,
        limit=None,
        page_size=1000
    ):
        if not api_key:
            raise ValueError("API 인증키가 필요합니다.")

        if not 1 <= page_size <= 1000:
            raise ValueError("잘못된 페이지 크기")

        if limit is not None and limit < 1:
            raise ValueError("조회 범위 오류")

        self._api_key = api_key
        self._limit = limit
        self._page_size = page_size

    def _request_page(self, start, end):
        url = (
            "http://openapi.seoul.go.kr:8088/"
            f"{self._api_key}/json/"
            f"SeoulPublicLibraryInfo/{start}/{end}/"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError):
            raise RuntimeError(
                "서울시 API 데이터 수신 실패"
            ) from None

        if not isinstance(data, dict):
            raise RuntimeError("잘못된 API 응답")

        service = data.get(
            "SeoulPublicLibraryInfo", {}
        )

        if not isinstance(service, dict):
            raise RuntimeError("잘못된 서비스 응답")

        result = service.get(
            "RESULT",
            data.get("RESULT", {})
        )

        if not isinstance(result, dict):
            raise RuntimeError("잘못된 결과 형식")

        code = result.get("CODE")

        if code == "INFO-200":
            return [], 0

        if code != "INFO-000":
            raise RuntimeError(
                f"API 요청 실패: {code}"
            )

        rows = service.get("row")

        if not isinstance(rows, list):
            raise RuntimeError("데이터 형식 오류")

        try:
            total = int(service["list_total_count"])
        except (KeyError, TypeError, ValueError):
            raise RuntimeError(
                "전체 데이터 수 확인 실패"
            ) from None

        if total < 0:
            raise RuntimeError("잘못된 전체 데이터 수")

        return rows, total

    def load(self) -> list[dict]:
        all_rows = []
        start = 1

        while True:
            end = start + self._page_size - 1

            if self._limit is not None:
                end = min(end, self._limit)

            rows, total = self._request_page(
                start, end
            )

            target = total

            if self._limit is not None:
                target = min(total, self._limit)

            if not rows:
                if start == 1 and target == 0:
                    return []

                raise RuntimeError(
                    "전체 데이터 수집 전 응답 종료"
                )

            all_rows.extend(rows)

            if len(all_rows) >= target:
                return all_rows[:target]

            start += len(rows)
