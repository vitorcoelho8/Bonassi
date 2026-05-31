class ParticipantSchema:
    required_fields = ("name", "phone")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "name": str(data["name"]).strip(),
            "phone": self._normalize_phone(data["phone"]),
        }

    def dump(self, participant) -> dict:
        return participant.to_dict()

    def dump_many(self, participants) -> list[dict]:
        return [self.dump(participant) for participant in participants]

    def _normalize_phone(self, value) -> str:
        phone = "".join(character for character in str(value) if character.isdigit())

        if len(phone) < 10:
            raise ValueError("Phone number must have at least 10 digits.")

        return phone


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
