from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ToolCall:
    tool_name: str
    arguments: Mapping[str, Any] = field(
        default_factory=dict
    )
    confirmed: bool = False
    call_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.tool_name,
            str,
        ):
            raise TypeError(
                "tool_name debe ser una "
                "cadena de caracteres."
            )

        normalized_name = (
            self.tool_name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "El nombre de la herramienta "
                "no puede estar vacío."
            )

        if not isinstance(
            self.arguments,
            Mapping,
        ):
            raise TypeError(
                "Los argumentos de la llamada "
                "deben ser un mapping."
            )

        if not isinstance(
            self.confirmed,
            bool,
        ):
            raise TypeError(
                "confirmed debe ser un valor "
                "booleano."
            )

        if not isinstance(
            self.call_id,
            str,
        ):
            raise TypeError(
                "call_id debe ser una cadena "
                "de caracteres."
            )

        normalized_call_id = (
            self.call_id.strip()
        )

        if not normalized_call_id:
            raise ValueError(
                "El identificador de la llamada "
                "no puede estar vacío."
            )

        object.__setattr__(
            self,
            "tool_name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "arguments",
            MappingProxyType(
                dict(self.arguments)
            ),
        )
        object.__setattr__(
            self,
            "call_id",
            normalized_call_id,
        )

    def with_confirmation(
        self,
    ) -> "ToolCall":
        return ToolCall(
            tool_name=self.tool_name,
            arguments=self.arguments,
            confirmed=True,
            call_id=self.call_id,
        )