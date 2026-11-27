
class SpatialAnalysisService:

    def get_nearby_libraries(
        self,
        libraries,
        origin,
        radius_km
    ):
        if radius_km <= 0:
            raise ValueError("반경은 0보다 커야 합니다.")

        results = []

        for library in libraries:
            distance = origin.calculate_distance(
                library.location
            )

            if distance <= radius_km:
                results.append({
                    "library": library,
                    "distance": distance
                })

        results.sort(
            key=lambda item: item["distance"]
        )

        return results

    def get_radius_statistics(
        self,
        libraries,
        origin,
        day,
        time,
        radii=(1, 3, 5)
    ):
        results = []

        for radius in radii:
            nearby = self.get_nearby_libraries(
                libraries,
                origin,
                radius
            )

            row = {
                "radius": radius,
                "total": len(nearby),
                "open": 0,
                "closed": 0,
                "unknown": 0
            }

            for item in nearby:
                library = item["library"]

                status = library.get_status(
                    time, day
                )

                row[status] += 1

            known = row["open"] + row["closed"]

            row["open_rate"] = (
                row["open"] / known * 100
                if known > 0
                else None
            )

            results.append(row)

        return results
