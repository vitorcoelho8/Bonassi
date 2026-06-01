from datetime import datetime

from app.matches.phases import is_knockout_phase, normalize_phase, phase_round_order


class MatchSchema:
    def load(self, data: dict) -> dict:
        home_team, away_team = self._parse_teams(data)
        phase = normalize_phase(data.get("phase"))
        round_order = self._parse_optional_int(data.get("round_order"))
        if round_order is None:
            round_order = phase_round_order(phase)
        is_brazil_match = self._parse_bool(data.get("is_brazil_match"), default=True)
        if is_brazil_match and not self._has_brazil(home_team, away_team):
            raise ValueError("Jogos do bolao devem envolver o Brasil.")

        return {
            "home_team": home_team,
            "away_team": away_team,
            "starts_at": self._parse_datetime(data.get("starts_at") or data.get("match_date")),
            "home_score": self._parse_optional_int(data.get("home_score")),
            "away_score": self._parse_optional_int(data.get("away_score")),
            "status": str(data.get("status") or "SCHEDULED").strip().upper(),
            "phase": phase,
            "round_order": round_order,
            "is_brazil_match": is_brazil_match,
            "is_knockout": self._parse_bool(data.get("is_knockout"), default=is_knockout_phase(phase)),
            "created_manually_by_admin": self._parse_bool(
                data.get("created_manually_by_admin"),
                default=True,
            ),
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

    def _parse_teams(self, data: dict) -> tuple[str, str]:
        home_team = self._optional_text(data.get("home_team"))
        away_team = self._optional_text(data.get("away_team"))
        if home_team and away_team:
            return home_team, away_team

        opponent = self._optional_text(data.get("opponent") or data.get("away_or_home_team"))
        if not opponent:
            raise ValueError("home_team e away_team sao obrigatorios.")

        brazil_is_home = self._parse_bool(
            data.get("brazil_is_home", data.get("is_brazil_home")),
            default=True,
        )
        if brazil_is_home:
            return "Brasil", opponent

        return opponent, "Brasil"

    def _parse_bool(self, value, default: bool) -> bool:
        if value in (None, ""):
            return default

        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            return bool(value)

        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "sim"}:
            return True

        if normalized in {"false", "0", "no", "nao"}:
            return False

        raise ValueError("Valor booleano invalido.")

    def _optional_text(self, value) -> str | None:
        if value in (None, ""):
            return None

        text = str(value).strip()
        return text or None

    def _has_brazil(self, home_team: str, away_team: str) -> bool:
        return "brasil" in {home_team.strip().lower(), away_team.strip().lower()}
