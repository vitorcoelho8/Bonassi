from app.bonus.models import BonusAnswer
from app.database import db


class BonusRepository:
    def list_by_participant(self, participant_id: str) -> list[BonusAnswer]:
        return BonusAnswer.query.filter_by(participant_id=participant_id).all()

    def get_answer(self, participant_id: str, question_key: str) -> BonusAnswer | None:
        return BonusAnswer.query.filter_by(
            participant_id=participant_id,
            question_key=question_key,
        ).first()

    def save(self, answer: BonusAnswer) -> BonusAnswer:
        db.session.add(answer)
        db.session.commit()
        return answer


class BonusService:
    def __init__(self, repository: BonusRepository | None = None) -> None:
        self.repository = repository or BonusRepository()

    def list_by_participant(self, participant_id: str) -> list[BonusAnswer]:
        return self.repository.list_by_participant(participant_id)

    def upsert(self, participant_id: str, data: dict) -> BonusAnswer:
        answer = self.repository.get_answer(participant_id, data["question_key"])

        if answer is None:
            answer = BonusAnswer(participant_id=participant_id, question_key=data["question_key"])

        answer.answer = data["answer"]
        return self.repository.save(answer)
