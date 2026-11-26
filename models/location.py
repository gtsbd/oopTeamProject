
import math


class Location:
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, lat: float, lon: float):
        if not -90 <= lat <= 90:
            raise ValueError("Invalid latitude")

        if not -180 <= lon <= 180:
            raise ValueError("Invalid longitude")

        self.lat = lat
        self.lon = lon

    def calculate_distance(self, other_loc: 'Location') -> float:
        lat1 = math.radians(self.lat)
        lat2 = math.radians(other_loc.lat)

        dlat = lat2 - lat1
        dlon = math.radians(other_loc.lon - self.lon)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        a = max(0.0, min(1.0, a))

        return (
            2 * self.EARTH_RADIUS_KM
            * math.asin(math.sqrt(a))
        )
