from collections.abc import Callable, Mapping
from typing import Any, TypeVar, cast

from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)


ToolFunction = Callable[..., Any]

F = TypeVar(
    "F",
    bound=ToolFunction,
)

_METADATA_ATTRIBUTE = "_tool_metadata"


def tool(
    name: str,
    description: str,
    parameters: Mapping[str, Any] | None = None,
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW,
    requires_confirmation: bool = False,
) -> Callable[[F], F]:
    metadata = ToolMetadata(
        name=name,
        description=description,
        parameters=(
            parameters
            if parameters is not None
            else {}
        ),
        risk_level=risk_level,
        requires_confirmation=(
            requires_confirmation
        ),
    )

    def decorator(function: F) -> F:
        setattr(
            function,
            _METADATA_ATTRIBUTE,
            metadata,
        )

        return cast(F, function)

    return decorator


def get_tool_metadata(
    function: Any,
) -> ToolMetadata | None:
    metadata = getattr(
        function,
        _METADATA_ATTRIBUTE,
        None,
    )

    if isinstance(
        metadata,
        ToolMetadata,
    ):
        return metadata

    return None


def get_tool_name(
    function: Any,
) -> str | None:
    metadata = get_tool_metadata(
        function
    )

    if metadata is None:
        return None

    return metadata.name