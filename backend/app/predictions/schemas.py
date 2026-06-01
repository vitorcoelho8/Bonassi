class PredictionSchema:
    required_fields = ("participant_id", "match_id", "home_score", "away_score")

    def load(self, data: dict) -> dict:
        normalized = {
            "participant_id": data.get("participant_id"),
            "match_id": data.get("match_id"),
            "home_score": data.get("predicted_home_score", data.get("home_score")),
            "away_score": data.get("predicted_away_score", data.get("away_score")),
        }
        missing = [field for field in self.required_fields if normalized.get(field) in (None, "")]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        home_score = int(normalized["home_score"])
        away_score = int(normalized["away_score"])
        if home_score < 0 or away_score < 0:
            raise ValueError("O placar nao pode ser negativo.")

        return {
            "participant_id": str(normalized["participant_id"]).strip(),
            "match_id": str(normalized["match_id"]).strip(),
            "home_score": home_score,
            "away_score": away_score,
        }

    def dump(self, prediction) -> dict:
        return prediction.to_dict()

    def dump_many(self, predictions) -> list[dict]:
        return [self.dump(prediction) for prediction in predictions]
