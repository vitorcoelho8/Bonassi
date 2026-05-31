class BonusAnswerSchema:
    required_fields = ("participant_id", "bonus_type", "evidence_text")
    allowed_bonus_types = {
        "FOLLOW_BONASSI",
        "STORY_MENTION",
        "INSTAGRAM_REVIEW",
        "REFERRAL",
    }

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        bonus_type = str(data["bonus_type"]).strip().upper()
        if bonus_type not in self.allowed_bonus_types:
            raise ValueError("Tipo de bonus invalido.")

        referral_name = self._optional_text(data.get("referral_name"))
        referral_phone = self._optional_phone(data.get("referral_phone"))

        if bonus_type == "REFERRAL" and (not referral_name or not referral_phone):
            raise ValueError("Nome e telefone do indicado sao obrigatorios.")

        return {
            "participant_id": str(data["participant_id"]).strip(),
            "bonus_type": bonus_type,
            "question_key": bonus_type,
            "evidence_text": str(data["evidence_text"]).strip(),
            "answer": str(data["evidence_text"]).strip(),
            "referral_name": referral_name,
            "referral_phone": referral_phone,
        }

    def dump(self, answer) -> dict:
        return answer.to_dict()

    def dump_many(self, answers) -> list[dict]:
        return [self.dump(answer) for answer in answers]

    def _optional_text(self, value) -> str | None:
        if value in (None, ""):
            return None

        return str(value).strip()

    def _optional_phone(self, value) -> str | None:
        if value in (None, ""):
            return None

        phone = "".join(character for character in str(value) if character.isdigit())
        if len(phone) < 10:
            raise ValueError("Telefone do indicado deve ter ao menos 10 digitos.")

        return phone
