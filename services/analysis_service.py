
class AnalysisService:

    def get_summary(self, libraries, day, time):
        result = {
            "total": len(libraries),
            "open": 0,
            "closed": 0,
            "unknown": 0
        }

        for library in libraries:
            status = library.get_status(time, day)
            result[status] += 1

        known = result["open"] + result["closed"]

        result["open_rate"] = (
            result["open"] / known * 100
            if known > 0
            else None
        )

        return result

    def get_hourly_statistics(self, libraries, day):
        results = []

        for hour in range(24):
            summary = self.get_summary(
                libraries, day, hour
            )

            results.append({
                "hour": hour,
                "open": summary["open"],
                "closed": summary["closed"],
                "unknown": summary["unknown"],
                "open_rate": summary["open_rate"]
            })

        return results

    def get_district_statistics(
        self, libraries, day, time
    ):
        groups = {}

        for library in libraries:
            district = library.district

            if district not in groups:
                groups[district] = []

            groups[district].append(library)

        results = []

        for district, group in sorted(groups.items()):
            summary = self.get_summary(
                group, day, time
            )

            results.append({
                "district": district,
                **summary
            })

        return results
