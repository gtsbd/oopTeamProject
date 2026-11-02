import unittest
from models.user import OfficeWorker, Student
from models.library import Library
from models.book import Book
from services.recommendation_service import RecommendationService

class TestRecommendationService(unittest.TestCase):
    def setUp(self):
        self.service = RecommendationService()

    def test_student_vs_worker_time_limit(self):
        # 기준 시각 18시, 19시 마감 도서관
        # 학생은 18시 도착(가능), 직장인은 19시 도착(불가능)
        lib = Library("테스트 도서관", 37.5, 127.0, 19)
        lib.add_book(Book("클린 코드", "12345"))
        libraries = [lib]
        
        student = Student(37.5, 127.0, 18)
        worker = OfficeWorker(37.5, 127.0, 18)
        
        # 학생 검증
        res_s = self.service.recommend_libraries(student, libraries, "클린 코드")
        self.assertEqual(res_s["total_count"], 1)
        
        # 직장인 검증 (19시 정각 도착은 마감으로 간주되어 제외됨)
        res_w = self.service.recommend_libraries(worker, libraries, "클린 코드")
        self.assertEqual(res_w["total_count"], 0)

    def test_book_availability_filtering(self):
        # 가까운 A는 책 없음, 먼 B는 책 있음
        lib_a = Library("가까운 A", 37.51, 127.01, 22)
        lib_b = Library("먼 B", 37.6, 127.1, 22)
        lib_b.add_book(Book("클린 코드", "12345"))
        
        libraries = [lib_a, lib_b]
        user = Student(37.5, 127.0, 10)
        
        res = self.service.recommend_libraries(user, libraries, "클린 코드")
        self.assertEqual(res["total_count"], 1)
        self.assertEqual(res["top_results"][0]["library"].name, "먼 B")

    def test_top_5_sorting_and_limit(self):
        # 6곳을 거리 역순(먼 곳부터)으로 입력해도 가까운 순으로 5곳만 반환되어야 함
        libraries = []
        for i in range(1, 7):
            # i가 커질수록 멀어짐
            lib = Library(f"도서관 {i}", 37.5 + (i*0.01), 127.0 + (i*0.01), 22)
            lib.add_book(Book("추천 도서", "isbn"))
            libraries.append(lib)
            
        # 역순으로 입력
        libraries.reverse()
        
        user = Student(37.5, 127.0, 10)
        res = self.service.recommend_libraries(user, libraries, "추천 도서")
        
        self.assertEqual(res["total_count"], 6)
        self.assertEqual(len(res["top_results"]), 5)
        # 가장 가까운 곳은 "도서관 1"이어야 함
        self.assertEqual(res["top_results"][0]["library"].name, "도서관 1")
        # 두 번째는 "도서관 2"
        self.assertEqual(res["top_results"][1]["library"].name, "도서관 2")

    def test_empty_or_no_match(self):
        # 도서관 목록이 비었거나 조건을 만족하는 곳이 없는 경우
        user = Student(37.5, 127.0, 10)
        
        # 빈 목록
        res_empty = self.service.recommend_libraries(user, [], "책")
        self.assertEqual(res_empty["total_count"], 0)
        self.assertEqual(len(res_empty["top_results"]), 0)
        
        # 조건 불일치 (책 없음)
        lib = Library("도서관", 37.5, 127.0, 22)
        res_no_match = self.service.recommend_libraries(user, [lib], "없는 책")
        self.assertEqual(res_no_match["total_count"], 0)

if __name__ == "__main__":
    unittest.main()
