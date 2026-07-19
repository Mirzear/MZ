from collections.abc import Callable
from typing import Any

from app.tools.tool_metadata import (
    ToolMetadata,
)


ToolHandler = Callable[..., Any]


class ToolRegistry:

    def __init__(self) -> None:
        self._handlers: dict[
            str,
            ToolHandler,
        ] = {}

        self._metadata: dict[
            str,
            ToolMetadata,
        ] = {}

    def register(
        self,
        metadata: ToolMetadata,
        handler: ToolHandler,
    ) -> None:
        tool_name = metadata.name

        if tool_name in self._handlers:
            raise ValueError(
                f"La herramienta '{tool_name}' "
                "ya está registrada."
            )

        if not callable(handler):
            raise TypeError(
                "El handler de la herramienta "
                "debe ser invocable."
            )

        self._handlers[
            tool_name
        ] = handler

        self._metadata[
            tool_name
        ] = metadata

    def get(
        self,
        tool_name: str,
    ) -> ToolHandler | None:
        normalized_name = (
            tool_name.strip().lower()
        )

        return self._handlers.get(
            normalized_name
        )

    def get_metadata(
        self,
        tool_name: str,
    ) -> ToolMetadata | None:
        normalized_name = (
            tool_name.strip().lower()
        )

        return self._metadata.get(
            normalized_name
        )

    def exists(
        self,
        tool_name: str,
    ) -> bool:
        normalized_name = (
            tool_name.strip().lower()
        )

        return (
            normalized_name
            in self._handlers
        )

    def get_tools(self) -> set[str]:
        return set(self._handlers)

    def get_all_metadata(
        self,
    ) -> tuple[ToolMetadata, ...]:
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