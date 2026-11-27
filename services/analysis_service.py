from models.user import Student, OfficeWorker
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
    
    def get_data_quality(self, libraries):
        result = {
            "total": len(libraries),
            "weekday_known": 0,
            "weekend_known": 0,
            "complete_hours": 0,
            "incomplete_hours": 0
        }

        for library in libraries:
            hours = library.operating_hours

            weekday_known = hours.weekday is not None
            weekend_known = hours.weekend is not None

            if weekday_known:
                result["weekday_known"] += 1

            if weekend_known:
                result["weekend_known"] += 1

            if weekday_known and weekend_known:
                result["complete_hours"] += 1
            else:
                result["incomplete_hours"] += 1

        return result

    def get_weekly_statistics(self, libraries):
        results = []

        days = [
            "월", "화", "수", "목",
            "금", "토", "일"
        ]

        for day in days:
            for hour in range(24):
                summary = self.get_summary(
                    libraries, day, hour
                )

                results.append({
                    "day": day,
                    "hour": hour,
                    "open": summary["open"],
                    "closed": summary["closed"],
                    "unknown": summary["unknown"],
                    "open_rate": summary["open_rate"]
                })

        return results
    
    def compare_user_types(self, libraries, day):
        results = []

        for hour in range(24):
            users = {
                "student": Student(37.5, 127.0, hour),
                "worker": OfficeWorker(37.5, 127.0, hour)
            }

            row = {"hour": hour}

            for user_type, user in users.items():
                available_time = user.get_available_time()

                if available_time >= 24:
                    row[user_type] = 0
                    continue

                summary = self.get_summary(
                    libraries,
                    day,
                    available_time
                )

                row[user_type] = summary["open"]

            results.append(row)

        return results


