from collections.abc import Callable

from app.commands.command_metadata import (
    CommandMetadata,
)


CommandHandler = Callable[[list[str]], None]


class CommandRegistry:

    def __init__(self) -> None:
        self._handlers: dict[
            str,
            CommandHandler,
        ] = {}

        self._metadata: dict[
            str,
            CommandMetadata,
        ] = {}

    def register(
        self,
        command: str,
        handler: CommandHandler,
        metadata: CommandMetadata | None = None,
    ) -> None:
        normalized_command = (
            command.strip().lower()
        )

        if not normalized_command:
            raise ValueError(
                "El nombre del comando "
                "no puede estar vacío."
            )

        if normalized_command in self._handlers:
            raise ValueError(
                f"El comando "
                f"'{normalized_command}' "
                "ya está registrado."
            )

        if not callable(handler):
            raise TypeError(
                "El handler del comando "
                "debe ser invocable."
            )

        if (
            metadata is not None
            and metadata.name
            != normalized_command
        ):
            raise ValueError(
                "El nombre de los metadatos "
                "no coincide con el comando "
                "registrado."
            )

        self._handlers[
            normalized_command
        ] = handler

        if metadata is not None:
            self._metadata[
                normalized_command
            ] = metadata

    def get(
        self,
        command: str,
    ) -> CommandHandler | None:
        normalized_command = (
            command.strip().lower()
        )

        return self._handlers.get(
            normalized_command
        )

    def get_metadata(
        self,
        command: str,
    ) -> CommandMetadata | None:
        normalized_command = (
            command.strip().lower()
        )

        return self._metadata.get(
            normalized_command
        )

    def exists(
        self,
        command: str,
    ) -> bool:
        normalized_command = (
            command.strip().lower()
        )

        return (
            normalized_command
            in self._handlers
        )

    def get_commands(self) -> set[str]:
        return set(self._handlers)

    def get_all_metadata(
        self,
    ) -> tuple[CommandMetadata, ...]:
        return tuple(
            sorted(
                self._metadata.values(),
                key=lambda metadata: (
                    metadata.name
                ),
            )
        )

    def count(self) -> int:
        return len(self._handlers)