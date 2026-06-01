from app.bonus.models import BonusAnswer
from app.database import db
from app.participants.models import Participant


BONUS_DESCRIPTIONS = {
    "FOLLOW_BONASSI": "Seguir a Bonassi",
    "STORY_MENTION": "Story marcando a clinica",
    "INSTAGRAM_REVIEW": "Avaliar/interagir com a Bonassi no Instagram",
    "REFERRAL": "Indicar alguem para fazer parte do time de pacientes",
}

BONUS_POINTS = {
    "FOLLOW_BONASSI": 4,
    "STORY_MENTION": 4,
    "INSTAGRAM_REVIEW": 2,
    "REFERRAL": 6,
}


class BonusRepository:
    def list_by_participant(self, participant_id: str) -> list[BonusAnswer]:
        return (
            BonusAnswer.query.filter_by(participant_id=participant_id)
            .order_by(BonusAnswer.created_at.desc())
            .all()
        )

    def list_pending(self) -> list[BonusAnswer]:
        return (
            BonusAnswer.query.filter_by(status="PENDING")
            .order_by(BonusAnswer.created_at.asc())
            .all()
        )

    def get_answer(self, participant_id: str, question_key: str) -> BonusAnswer | None:
        return BonusAnswer.query.filter_by(
            participant_id=participant_id,
            question_key=question_key,
        ).first()

    def get_by_id(self, bonus_id: str) -> BonusAnswer | None:
        return db.session.get(BonusAnswer, bonus_id)

    def save(self, answer: BonusAnswer) -> BonusAnswer:
        db.session.add(answer)
        db.session.commit()
        return answer


class BonusService:
    def __init__(self, repository: BonusRepository | None = None) -> None:
        self.repository = repository or BonusRepository()

    def list_by_participant(self, participant_id: str) -> list[BonusAnswer]:
        return self.repository.list_by_participant(participant_id)

    def list_pending(self) -> list[BonusAnswer]:
        return self.repository.list_pending()

    def upsert(self, data: dict) -> BonusAnswer:
        participant = db.session.get(Participant, data["participant_id"])
        if participant is None or not participant.is_active or participant.role != "participant":
            raise ValueError("Participante nao encontrado.")

        answer = self.repository.get_answer(participant.id, data["question_key"])

        if answer is None:
            answer = BonusAnswer(participant_id=participant.id, question_key=data["question_key"])
        elif answer.status == "APPROVED":
            raise ValueError("Este bonus ja foi aprovado para o participante.")

        answer.bonus_type = data["bonus_type"]
        answer.evidence_text = data["evidence_text"]
        answer.referral_name = data["referral_name"]
        answer.referral_phone = data["referral_phone"]
        answer.status = "PENDING"
        answer.points = BONUS_POINTS[data["bonus_type"]]
        answer.answer = data["answer"]
        return self.repository.save(answer)

    def approve(self, bonus_id: str) -> BonusAnswer:
        answer = self.repository.get_by_id(bonus_id)
        if answer is None:
            raise ValueError("Solicitacao de bonus nao encontrada.")

        answer.status = "APPROVED"
        return self.repository.save(answer)

    def reject(self, bonus_id: str) -> BonusAnswer:
        answer = self.repository.get_by_id(bonus_id)
        if answer is None:
            raise ValueError("Solicitacao de bonus nao encontrada.")

        answer.status = "REJECTED"
        return self.repository.save(answer)
