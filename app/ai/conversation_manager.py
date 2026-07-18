class ConversationManager:

    VALID_ROLES = {
        "user",
        "assistant",
    }

    def __init__(self, max_messages: int = 20) -> None:
        if max_messages <= 0:
            raise ValueError(
                "max_messages debe ser mayor que cero."
            )

        self.max_messages = max_messages
        self.messages: list[dict[str, str]] = []

    def add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        normalized_role = role.strip().lower()
        cleaned_content = content.strip()

        if normalized_role not in self.VALID_ROLES:
            raise ValueError(
                f"Rol de conversación inválido: '{role}'."
            )

        if not cleaned_content:
            raise ValueError(
                "El contenido del mensaje no puede estar vacío."
            )

        self.messages.append(
            {
                "role": normalized_role,
                "content": cleaned_content,
            }
        )

        self._apply_limit()

    def get_messages(self) -> list[dict[str, str]]:
        return [
            message.copy()
            for message in self.messages
        ]

    def clear(self) -> None:
        self.messages.clear()

    def count(self) -> int:
        return len(self.messages)

    def _apply_limit(self) -> None:
        excess = len(self.messages) - self.max_messages

        if excess > 0:
            del self.messages[:excess]