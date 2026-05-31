class RegisterUserSchema:
    required_fields = ("name", "email", "password")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "name": data["name"].strip(),
            "email": data["email"].strip().lower(),
            "password": data["password"],
        }


class LoginSchema:
    required_fields = ("email", "password")

    def load(self, data: dict) -> dict:
        missing = [field for field in self.required_fields if not data.get(field)]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return {
            "email": data["email"].strip().lower(),
            "password": data["password"],
        }
