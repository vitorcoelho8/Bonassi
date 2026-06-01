from datetime import datetime


class MatchSchema:
    required_fields = ("home_team", "away_team")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "home_team": str(data["home_team"]).strip(),
            "away_team": str(data["away_team"]).strip(),
            "starts_at": self._parse_datetime(data.get("starts_at") or data.get("match_date")),
            "home_score": self._parse_optional_int(data.get("home_score")),
            "away_score": self._parse_optional_int(data.get("away_score")),
            "status": str(data.get("status") or "SCHEDULED").strip().upper(),
        }

    def dump(self, match) -> dict:
        return match.to_dict()

    def dump_many(self, matches) -> list[dict]:
        return [self.dump(match) for match in matches]

    def _parse_datetime(self, value):
        if not value:
            return None

        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    def _parse_optional_int(self, value):
        if value is None or value == "":
            return None

        return int(value)
