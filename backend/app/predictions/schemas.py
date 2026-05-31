class PredictionSchema:
    required_fields = ("match_id", "home_score", "away_score")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if data.get(field) in (None, "")]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "match_id": str(data["match_id"]).strip(),
            "home_score": int(data["home_score"]),
            "away_score": int(data["away_score"]),
        }

    def dump(self, prediction) -> dict:
        return prediction.to_dict()

    def dump_many(self, predictions) -> list[dict]:
        return [self.dump(prediction) for prediction in predictions]
