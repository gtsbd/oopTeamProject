from typing import List, Dict, Any
from models.user import User
from models.library import Library


class RecommendationService:

    def recommend_libraries(
        self,
        user,
        libraries,
        book_title,
        day="월"
    ):
        avail_time = user.get_available_time()
        results = []

        # 기존 정책: 자정 이후 방문은 추천하지 않음
        if not 0 <= avail_time < 24:
            return {
                "total_count": 0,
                "top_results": []
            }

        for library in libraries:
            if not library.is_open(avail_time, day):
                continue

            if not library.has_book(book_title):
                continue

            distance = user.location.calculate_distance(
                library.location
            )

            results.append({
                "library": library,
                "distance": distance,
                "available_time": avail_time,
                "close_time": library.get_close_time(day)
            })

        results.sort(
            key=lambda item: item["distance"]
        )

        return {
            "total_count": len(results),
            "top_results": results[:5]
        }
