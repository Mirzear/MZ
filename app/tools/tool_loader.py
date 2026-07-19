from collections.abc import Iterable
from typing import Any

from app.tools.tool_decorator import (
    get_tool_metadata,
)
from app.tools.tool_metadata import (
    ToolMetadata,
)
from app.tools.tool_registry import (
    ToolHandler,
    ToolRegistry,
)


class ToolLoader:

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        self._registry = registry

    def load(
        self,
        provider: Any,
    ) -> int:
        return self.load_many(
            (provider,)
        )

    def load_many(
        self,
        providers: Iterable[Any],
    ) -> int:
        discovered_tools: dict[
            str,
            tuple[
                ToolMetadata,
                ToolHandler,
            ],
        ] = {}

        for provider in providers:
            provider_tools = (
                self._discover(provider)
            )

            for metadata, handler in (
                provider_tools
            ):
                tool_name = metadata.name

                if (
                    tool_name
                    in discovered_tools
                ):
                    raise ValueError(
                        f"La herramienta "
                        f"'{tool_name}' fue "
                        "descubierta más de "
                        "una vez."
                    )

                if self._registry.exists(
                    tool_name
                ):
                    raise ValueError(
                        f"La herramienta "
                        f"'{tool_name}' ya está "
                        "registrada."
                    )

                discovered_tools[
                    tool_name
                ] = (
                    metadata,
                    handler,
                )

        for tool_name in sorted(
            discovered_tools
        ):
            metadata, handler = (
                discovered_tools[
                    tool_name
                ]
            )

            self._registry.register(
                metadata=metadata,
                handler=handler,
            )

        return len(discovered_tools)

    def _discover(
        self,
        provider: Any,
    ) -> tuple[
        tuple[
            ToolMetadata,
            ToolHandler,
        ],
        ...,
    ]:
        discovered_tools: list[
            tuple[
                ToolMetadata,
                ToolHandler,
            ]
        ] = []

        for attribute_name in dir(
            provider
        ):
            if attribute_name.startswith(
                "_"
            ):
                continue

            attribute = getattr(
                provider,
                attribute_name,
            )

            if not callable(attribute):
                continue

            metadata = get_tool_metadata(
                attribute
            )

            if metadata is None:
                continue

            discovered_tools.append(
                (
                    metadata,
                    attribute,
                )
            )

        return tuple(
            discovered_tools
        )