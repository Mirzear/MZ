from app.ai.conversation_message import (
    ConversationMessage,
    ConversationRole,
)


class ConversationManager:
    VALID_ROLES = frozenset(
        role.value
        for role in ConversationRole
    )

    def __init__(
        self,
        max_messages: int = 20,
    ) -> None:
        if (
            not isinstance(max_messages, int)
            or isinstance(max_messages, bool)
        ):
            raise TypeError(
                "max_messages debe ser un número entero."
            )

        if max_messages <= 0:
            raise ValueError(
                "max_messages debe ser mayor que cero."
            )

        self.max_messages = max_messages
        self._messages: list[
            ConversationMessage
        ] = []

    @property
    def messages(
        self,
    ) -> list[ConversationMessage]:
        return list(self._messages)

    def add_message(
        self,
        role: ConversationRole | str,
        content: str,
    ) -> None:
        message = ConversationMessage(
            role=ConversationRole.from_value(role),
            content=content,
        )

        self.add(message)

    def add(
        self,
        message: ConversationMessage,
    ) -> None:
        if not isinstance(
            message,
            ConversationMessage,
        ):
            raise TypeError(
                "message debe ser una instancia de "
                "ConversationMessage."
            )

        self._messages.append(message)
        self._apply_limit()

    def get_messages(
        self,
    ) -> list[dict[str, str]]:
        """
        Return messages using the legacy dictionary format.

        This keeps compatibility with AI providers that currently
        expect list[dict[str, str]].
        """
        return [
            message.to_dict()
            for message in self._messages
        ]

    def get_message_objects(
        self,
    ) -> list[ConversationMessage]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def count(self) -> int:
        return len(self._messages)

    def _apply_limit(self) -> None:
        excess = (
            len(self._messages)
            - self.max_messages
        )

        if excess > 0:
            del self._messages[:excess]