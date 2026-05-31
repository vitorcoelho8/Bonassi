class BonusAnswerSchema:
    required_fields = ("question_key", "answer")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "question_key": str(data["question_key"]).strip(),
            "answer": str(data["answer"]).strip(),
        }

    def dump(self, answer) -> dict:
        return answer.to_dict()

    def dump_many(self, answers) -> list[dict]:
        return [self.dump(answer) for answer in answers]
