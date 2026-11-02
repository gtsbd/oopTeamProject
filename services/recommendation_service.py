from typing import List, Dict, Any
from models.user import User
from models.library import Library

class RecommendationService:
    """
    도서관 추천 로직을 담당하는 서비스 클래스.
    UI(Streamlit)에 의존하지 않으며, 도메인 모델 간의 상호작용을 관리함.
    """
    def recommend_libraries(self, user: User, libraries: List[Library], book_title: str) -> Dict[str, Any]:
        """
        사용자의 위치와 시각, 희망 도서를 바탕으로 최적의 도서관을 추천함.
        """
        avail_time = user.get_available_time()
        results = []
        
        for lib in libraries:
            # 1. 거리 계산 (Location 객체 위임)
            dist = user.location.calculate_distance(lib.location)
            
            # 2. 운영 여부 및 도서 보유 여부 확인 (Library 객체 위임)
            if lib.is_open(avail_time) and lib.has_book(book_title):
                results.append({
                    "library": lib,
                    "distance": dist,
                    "available_time": avail_time,
                    "close_time": lib.close_time
                })
                
        # 3. 거리순 정렬 (거리가 같을 경우 기존 리스트 순서 보존)
        results.sort(key=lambda x: x["distance"])
        
        return {
            "total_count": len(results),
            "top_results": results[:5]
        }
