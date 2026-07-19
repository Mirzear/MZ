from collections.abc import Callable
from datetime import datetime
from typing import Any

from app.tools.tool_decorator import tool
from app.tools.tool_metadata import (
    ToolRiskLevel,
)


DateTimeProvider = Callable[[], datetime]


class CoreTools:

    def __init__(
        self,
        datetime_provider: (
            DateTimeProvider | None
        ) = None,
    ) -> None:
        self._datetime_provider = (
            datetime_provider
            if datetime_provider is not None
            else self._get_local_datetime
        )

    @tool(
        name="get_current_datetime",
        description=(
            "Obtiene la fecha y hora "
            "local actual."
        ),
        risk_level=ToolRiskLevel.LOW,
        requires_confirmation=False,
    )
    def get_current_datetime(
        self,
    ) -> str:
        current_datetime = (
            self._datetime_provider()
        )

        if not isinstance(
            current_datetime,
            datetime,
        ):
            raise TypeError(
                "El proveedor de fecha y "
                "hora debe devolver una "
                "instancia de datetime."
            )

        return current_datetime.isoformat(
            timespec="seconds"
        )

    @tool(
        name="count_words",
        description=(
            "Cuenta la cantidad de "
            "palabras de un texto."
        ),
        parameters={
            "text": {
                "type": "string",
                "description": (
                    "Texto cuyas palabras "
                    "se contarán."
                ),
                "required": True,
            },
        },
        risk_level=ToolRiskLevel.LOW,
        requires_confirmation=False,
    )
    def count_words(
        self,
        text: str,
    ) -> int:
        if not isinstance(text, str):
            raise TypeError(
                "El texto debe ser una "
                "cadena de caracteres."
            )

        return len(
            text.split()
        )

    @staticmethod
    def _get_local_datetime() -> datetime:
        return datetime.now().astimezone()