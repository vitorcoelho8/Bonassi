class TeamSchema:
    def dump(self, team) -> dict:
        return team.to_dict()

    def dump_many(self, teams) -> list[dict]:
        return [self.dump(team) for team in teams]
