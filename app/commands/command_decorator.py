from collections.abc import Callable
from typing import Any, TypeVar, cast


CommandMethod = Callable[..., None]
F = TypeVar("F", bound=CommandMethod)


def command(name: str) -> Callable[[F], F]:
    normalized_name = name.strip().lower()

    if not normalized_name:
        raise ValueError(
            "El nombre del comando no puede estar vacío."
        )

    def decorator(function: F) -> F:
        setattr(
            function,
            "_command_name",
            normalized_name,
        )

        return cast(F, function)

    return decorator


def get_command_name(
    function: Any,
) -> str | None:
    return getattr(
        function,
        "_command_name",
        None,
    )