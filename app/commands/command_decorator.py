from collections.abc import Callable
from typing import Any, TypeVar, cast

from app.commands.command_metadata import (
    CommandMetadata,
)


CommandMethod = Callable[..., None]
F = TypeVar(
    "F",
    bound=CommandMethod,
)

_METADATA_ATTRIBUTE = "_command_metadata"


def command(
    name: str,
    usage: str | None = None,
    description: str | None = None,
) -> Callable[[F], F]:
    normalized_name = name.strip().lower()

    if not normalized_name:
        raise ValueError(
            "El nombre del comando "
            "no puede estar vacío."
        )

    normalized_usage = (
        usage.strip()
        if usage is not None
        else normalized_name
    )

    normalized_description = (
        description.strip()
        if description is not None
        else f"Ejecuta el comando "
        f"'{normalized_name}'."
    )

    metadata = CommandMetadata(
        name=normalized_name,
        usage=normalized_usage,
        description=normalized_description,
    )

    def decorator(function: F) -> F:
        setattr(
            function,
            _METADATA_ATTRIBUTE,
            metadata,
        )

        return cast(F, function)

    return decorator


def get_command_metadata(
    function: Any,
) -> CommandMetadata | None:
    metadata = getattr(
        function,
        _METADATA_ATTRIBUTE,
        None,
    )

    if isinstance(
        metadata,
        CommandMetadata,
    ):
        return metadata

    return None


def get_command_name(
    function: Any,
) -> str | None:
    metadata = get_command_metadata(
        function
    )

    if metadata is None:
        return None

    return metadata.name