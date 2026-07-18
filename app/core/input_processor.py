class InputProcessor:

    def normalize(self, user_input: str) -> str:
        """Normalize raw user input."""
        return " ".join(user_input.strip().split())

    def split(self, user_input: str) -> list[str]:
        """Split normalized input into command, key and value."""
        normalized_input = self.normalize(user_input)

        if not normalized_input:
            return []

        return normalized_input.split(maxsplit=2)

    def get_command(self, parts: list[str]) -> str:
        """Return the command in lowercase."""
        if not parts:
            return ""

        return parts[0].lower()