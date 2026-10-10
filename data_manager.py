import requests
import random
from models.library import Library
from models.book import Book

class SystemManager:
    def __init__(self):
        self.libraries = []
        # 발급받은 실제 인증키 적용
        self.api_key = "6a6b554f7277687232357741677367"
        self._load_real_data_from_api()

    def _load_real_data_from_api(self):
        # API 호출 (일단 100개만 불러오도록 설정)
        url = f"http://openapi.seoul.go.kr:8088/{self.api_key}/json/SeoulPublicLibraryInfo/1/100/"
        
        try:
            response = requests.get(url)
            data = response.json()
            rows = data.get("SeoulPublicLibraryInfo", {}).get("row", [])
            
            for row in rows:
                name = row.get("LBRRY_NAME", "이름없음")
                lat_str = row.get("XCNTS", "0")
                lon_str = row.get("YDNTS", "0")
                op_time_str = row.get("OP_TIME", "18:00")
                
                lat = float(lat_str) if lat_str != "" else 0.0
                lon = float(lon_str) if lon_str != "" else 0.0
                close_time = self._parse_close_time(op_time_str)
                
                if lat == 0.0 or lon == 0.0:
                    continue
                
                real_library = Library(name, lat, lon, close_time)
                self._inject_dummy_books(real_library)
                simulated_max_seats = random.randint(50, 200)
                simulated_popularity = round(random.uniform(0.8, 1.2), 2)
                
                real_library.set_capacity(simulated_max_seats, simulated_popularity)
                
                self.libraries.append(real_library)
                
        except Exception as e:
            print(f"API 데이터 로드 실패: {e}")

    def _parse_close_time(self, time_str: str) -> int:
        try:
            if "~" in time_str:
                end_part = time_str.split("~")[1].strip()
                return int(end_part[:2])
            return 18 
        except:
            return 18

    def _inject_dummy_books(self, library: Library):
        best_sellers = ["이기적 유전자", "사피엔스", "클린 코드", "코스모스", "총균쇠"]
        available_books = random.sample(best_sellers, random.randint(2, 4))
        for title in available_books:
            library.add_book(Book(title, "Dummy-ISBN"))

    def get_libraries(self):
        return self.libraries