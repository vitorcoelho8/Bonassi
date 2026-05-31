class CompetitionSchema:
    required_fields = ("name", "season")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "name": data["name"].strip(),
            "season": str(data["season"]).strip(),
        }

    def dump(self, data) -> dict:
        return data.to_dict()

    def dump_many(self, data) -> list[dict]:
        return [item.to_dict() for item in data]
