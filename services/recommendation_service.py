
class RecommendationService:

    def recommend_libraries(
        self,
        user,
        libraries,
        book_title=None,
        day="월",
        radius_km=None
    ):
        if radius_km is not None and radius_km <= 0:
            raise ValueError("잘못된 검색 반경입니다.")

        avail_time = user.get_available_time()
        results = []

        if not 0 <= avail_time < 24:
            return {
                "total_count": 0,
                "top_results": []
            }

        for library in libraries:

            # 1. 운영 여부 확인
            if not library.is_open(avail_time, day):
                continue

            # 2. 도서 조건이 있는 경우만 검사
            if book_title is not None:
                if not library.has_book(book_title):
                    continue

            # 3. 거리 계산
            distance = user.location.calculate_distance(
                library.location
            )

            # 4. 검색 반경 확인
            if radius_km is not None:
                if distance > radius_km:
                    continue

            results.append({
                "library": library,
                "distance": distance,
                "available_time": avail_time,
                "close_time": library.get_close_time(day)
            })

        # 5. 거리순 정렬
        results.sort(
            key=lambda item: item["distance"]
        )

        return {
            "total_count": len(results),
            "top_results": results[:5]
        }
