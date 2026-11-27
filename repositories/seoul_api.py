
import requests

from repositories.base import LibraryRepository


class SeoulAPIRepository(LibraryRepository):

    def __init__(self, api_key: str, limit: int = 100):
        if not api_key:
            raise ValueError("API 인증키가 필요합니다.")

        if not 1 <= limit <= 1000:
            raise ValueError("조회 범위는 1~1000입니다.")

        self._api_key = api_key
        self._limit = limit

    def load(self) -> list[dict]:
        url = (
            "http://openapi.seoul.go.kr:8088/"
            f"{self._api_key}/json/"
            f"SeoulPublicLibraryInfo/1/{self._limit}/"
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
            raise RuntimeError("잘못된 API 응답 형식입니다.")

        service = data.get("SeoulPublicLibraryInfo", {})

        if not isinstance(service, dict):
            raise RuntimeError("잘못된 서비스 응답입니다.")

        result = service.get("RESULT", data.get("RESULT", {}))
        code = result.get("CODE")

        if code == "INFO-200":
            return []

        if code and code != "INFO-000":
            raise RuntimeError(
                f"API 요청 실패: {code}"
            )

        rows = service.get("row")

        if not isinstance(rows, list):
            raise RuntimeError("도서관 데이터 형식 오류")

        return rows
