class PredictionSchema:
    required_fields = ("participant_id", "match_id")

    def load(self, data: dict) -> dict:
        uses_brazil_scores = "brazil_score" in data or "opponent_score" in data
        normalized = {
            "participant_id": data.get("participant_id"),
            "match_id": data.get("match_id"),
        }
        missing = [field for field in self.required_fields if normalized.get(field) in (None, "")]

        if uses_brazil_scores:
            normalized["brazil_score"] = data.get("brazil_score")
            normalized["opponent_score"] = data.get("opponent_score")
            missing.extend(
                field
                for field in ("brazil_score", "opponent_score")
                if normalized.get(field) in (None, "")
            )
        else:
            normalized["home_score"] = data.get("predicted_home_score", data.get("home_score"))
            normalized["away_score"] = data.get("predicted_away_score", data.get("away_score"))
            missing.extend(
                field
                for field in ("home_score", "away_score")
                if normalized.get(field) in (None, "")
            )

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        payload = {
            "participant_id": str(normalized["participant_id"]).strip(),
            "match_id": str(normalized["match_id"]).strip(),
        }

        if uses_brazil_scores:
            payload["brazil_score"] = self._parse_score(normalized["brazil_score"])
            payload["opponent_score"] = self._parse_score(normalized["opponent_score"])
            return payload

        payload["home_score"] = self._parse_score(normalized["home_score"])
        payload["away_score"] = self._parse_score(normalized["away_score"])
        return payload

    def dump(self, prediction) -> dict:
        data = prediction.to_dict()
        match = getattr(prediction, "match", None)
        if match is None:
            return data

        data["home_team"] = match.home_team
        data["away_team"] = match.away_team
        brazil_context = self._brazil_context(match.home_team, match.away_team)
        if brazil_context is None:
            return data

        opponent_team, brazil_is_home = brazil_context
        brazil_score = prediction.home_score if brazil_is_home else prediction.away_score
        opponent_score = prediction.away_score if brazil_is_home else prediction.home_score
        data.update(
            {
                "brazil_score": brazil_score,
                "opponent_score": opponent_score,
                "opponent_team": opponent_team,
                "display_prediction": f"Brasil {brazil_score} x {opponent_score} {opponent_team}",
            }
        )
        return data

    def dump_many(self, predictions) -> list[dict]:
        return [self.dump(prediction) for prediction in predictions]

    def _parse_score(self, value) -> int:
        if isinstance(value, bool):
            raise ValueError("O placar deve ser um numero inteiro.")

        if isinstance(value, float) and not value.is_integer():
            raise ValueError("O placar deve ser um numero inteiro.")

        if isinstance(value, str) and not value.strip().isdigit():
            raise ValueError("O placar deve ser um numero inteiro.")

        try:
            score = int(value)
        except (TypeError, ValueError) as error:
            raise ValueError("O placar deve ser um numero inteiro.") from error

        if score < 0:
            raise ValueError("O placar nao pode ser negativo.")

        return score

    def _brazil_context(self, home_team: str, away_team: str) -> tuple[str, bool] | None:
        if str(home_team or "").strip().lower() == "brasil":
            return away_team, True

        if str(away_team or "").strip().lower() == "brasil":
            return home_team, False

        return None
