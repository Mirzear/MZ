from collections.abc import Callable


CommandHandler = Callable[[list[str]], None]


class CommandRegistry:

    def __init__(self) -> None:
        self._handlers: dict[str, CommandHandler] = {}

    def register(
        self,
        command: str,
        handler: CommandHandler,
    ) -> None:
        normalized_command = command.strip().lower()

        if not normalized_command:
            raise ValueError(
                "El nombre del comando no puede estar vacío."
            )

        if normalized_command in self._handlers:
            raise ValueError(
                f"El comando '{normalized_command}' "
                "ya está registrado."
            )

        if not callable(handler):
            raise TypeError(
                "El handler del comando debe ser invocable."
            )

        self._handlers[normalized_command] = handler

    def get(
        self,
        command: str,
    ) -> CommandHandler | None:
        normalized_command = command.strip().lower()

        return self._handlers.get(normalized_command)

    def exists(self, command: str) -> bool:
        normalized_command = command.strip().lower()

        return normalized_command in self._handlers

    def get_commands(self) -> set[str]:
        return set(self._handlers)

    def count(self) -> int:
        return len(self._handlers)