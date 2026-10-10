from models.location import Location
from models.book import Book

class Library:
    def __init__(self, name: str, lat: float, lon: float, close_time: int):
        self.name = name
        self.location = Location(lat, lon)
        self.close_time = close_time
        self.books = []
        
        # 좌석 시뮬레이션을 위한 속성
        self.max_seats = 0      
        self.popularity = 1.0    # 0.8 ~ 1.2 사이의 도서관별 고유 인기도

    def set_capacity(self, max_seats: int, popularity: float):
        """총 좌석 수와 인기도 통계 가중치를 설정"""
        self.max_seats = max_seats
        self.popularity = popularity

    def get_congestion_rate(self, current_time: int) -> float:
        """[캡슐화] 요청받은 '시간'을 바탕으로 통계적 혼잡도(%)를 동적 연산"""
        # 1. 오픈 전이거나 마감 이후면 0%
        if current_time >= self.close_time or current_time < 9:
            return 0.0 
            
        # 2. 시간대별 통계 패턴 가중치 (실제 도서관 이용 패턴 반영)
        if 9 <= current_time <= 11:
            base_rate = 0.45  # 오전 (45%)
        elif 12 <= current_time <= 17:
            base_rate = 0.90  # 낮 피크타임 (90%)
        elif 18 <= current_time <= 19:
            base_rate = 0.60  # 저녁 식사 시간대 감소 (60%)
        else:
            base_rate = 0.75  # 야간 학업 시간 (75%)
            
        # 3. 시간대 기본값 * 도서관 고유 인기도
        final_rate = (base_rate * self.popularity) * 100
        
        # 최대 100%를 넘지 않도록 방어 코드
        return min(final_rate, 100.0)

    def is_crowded(self, current_time: int) -> bool:
        """혼잡도가 85% 이상인지 판별"""
        return self.get_congestion_rate(current_time) >= 85.0

    def add_book(self, book: Book):
        self.books.append(book)

    def is_open(self, user_time: int) -> bool:
        return user_time < self.close_time
        
    def has_book(self, target_title: str) -> bool:
        for book in self.books:
            if book.title == target_title and book.check_available():
                return True
        return False