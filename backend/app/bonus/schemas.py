from app.bonus.service import BONUS_DESCRIPTIONS


class BonusAnswerSchema:
    required_fields = ("participant_id", "bonus_type")
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

        participant_id = str(data["participant_id"]).strip()
        if not participant_id:
            raise ValueError("participant_id e obrigatorio.")

        bonus_type = str(data["bonus_type"]).strip().upper()
        if bonus_type not in self.allowed_bonus_types:
            raise ValueError("Tipo de bonus invalido.")

        evidence_text = self._optional_text(data.get("evidence_text")) or BONUS_DESCRIPTIONS.get(
            bonus_type,
            bonus_type,
        )
        referral_name = self._optional_text(data.get("referral_name"))
        referral_phone = self._optional_phone(data.get("referral_phone"))

        if bonus_type == "REFERRAL" and (not referral_name or not referral_phone):
            raise ValueError("Nome e telefone do indicado sao obrigatorios.")

        return {
            "participant_id": participant_id,
            "bonus_type": bonus_type,
            "question_key": bonus_type,
            "evidence_text": evidence_text,
            "answer": evidence_text,
            "referral_name": referral_name,
            "referral_phone": referral_phone,
        }

    def dump(self, answer, include_participant: bool = False) -> dict:
        data = answer.to_dict()
        data["description"] = BONUS_DESCRIPTIONS.get(answer.bonus_type, answer.bonus_type)
        data["created_at"] = answer.created_at.isoformat() if answer.created_at else None
        data["updated_at"] = answer.updated_at.isoformat() if answer.updated_at else None

        if include_participant:
            data["participant"] = answer.participant.to_dict() if answer.participant else None

        return data

    def dump_many(self, answers, include_participant: bool = False) -> list[dict]:
        return [self.dump(answer, include_participant=include_participant) for answer in answers]

    def _optional_text(self, value) -> str | None:
        if value in (None, ""):
            return None

        text = str(value).strip()
        return text or None

    def _optional_phone(self, value) -> str | None:
        if value in (None, ""):
            return None

        phone = "".join(character for character in str(value) if character.isdigit())
        if len(phone) < 10:
            raise ValueError("Telefone do indicado deve ter ao menos 10 digitos.")

        return phone
