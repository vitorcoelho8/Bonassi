class ParticipantSchema:
    required_fields = ("name", "email", "password")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "name": str(data["name"]).strip(),
            "email": str(data["email"]).strip().lower(),
            "password": str(data["password"]),
        }

    def dump(self, participant) -> dict:
        return participant.to_dict()

    def dump_many(self, participants) -> list[dict]:
        return [self.dump(participant) for participant in participants]


class LoginSchema:
    required_fields = ("email", "password")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "email": str(data["email"]).strip().lower(),
            "password": str(data["password"]),
        }
