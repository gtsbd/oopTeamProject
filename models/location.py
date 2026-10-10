import math

class Location:
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        
    def calculate_distance(self, other_loc: 'Location') -> float:
        # 피타고라스 공식을 이용한 단순 거리 연산 (100을 곱해 대략적인 km로 환산)
        return math.sqrt((self.lat - other_loc.lat)**2 + (self.lon - other_loc.lon)**2) * 100