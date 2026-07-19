from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ToolExecutionStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    CONFIRMATION_REQUIRED = (
        "confirmation_required"
    )


@dataclass(frozen=True, slots=True)
class ToolExecutionResult:
    tool_name: str
    status: ToolExecutionStatus
    output: Any = None
    error_message: str | None = None
    call_id: str | None = None

    def __post_init__(self) -> None:
        normalized_name = (
            self.tool_name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "El nombre de la herramienta "
                "no puede estar vacío."
            )

        if not isinstance(
            self.status,
            ToolExecutionStatus,
        ):
            raise TypeError(
                "El estado de ejecución debe "
                "ser un ToolExecutionStatus."
            )

        if (
            self.status
            is ToolExecutionStatus.SUCCESS
            and self.error_message is not None
        ):
            raise ValueError(
                "Una ejecución exitosa no puede "
                "contener un mensaje de error."
            )

        if (
            self.status
            is not ToolExecutionStatus.SUCCESS
            and not self.error_message
        ):
            raise ValueError(
                "Una ejecución no exitosa debe "
                "contener un mensaje de error."
            )

        normalized_call_id = self.call_id

        if normalized_call_id is not None:
            if not isinstance(
                normalized_call_id,
                str,
            ):
                raise TypeError(
                    "call_id debe ser una cadena "
                    "de caracteres o None."
                )

            normalized_call_id = (
                normalized_call_id.strip()
            )

            if not normalized_call_id:
                raise ValueError(
                    "call_id no puede ser una "
                    "cadena vacía."
                )

        object.__setattr__(
            self,
            "tool_name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "call_id",
            normalized_call_id,
        )

    @property
    def succeeded(self) -> bool:
        return (
            self.status
            is ToolExecutionStatus.SUCCESS
        )

    @property
    def requires_confirmation(self) -> bool:
        return (
            self.status
            is ToolExecutionStatus
            .CONFIRMATION_REQUIRED
        )