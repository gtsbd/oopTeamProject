from models.location import Location

class User:
    def __init__(self, lat: float, lon: float, base_time: int):
        self.location = Location(lat, lon)
        self.base_time = base_time
        
    def get_available_time(self) -> int:
        raise NotImplementedError("자식 클래스에서 오버라이딩 해야 합니다.")

class OfficeWorker(User):
    def get_available_time(self) -> int:
        return self.base_time + 1  # 직장인은 퇴근 후 이동 1시간 추가

class Student(User):
    def get_available_time(self) -> int:
        return self.base_time  # 학생은 하교 후 즉시 이용 가능