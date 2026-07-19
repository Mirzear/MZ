from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping


class ToolRiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class ToolMetadata:
    name: str
    description: str
    parameters: Mapping[str, Any]
    risk_level: ToolRiskLevel
    requires_confirmation: bool

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().lower()
        normalized_description = (
            self.description.strip()
        )

        if not normalized_name:
            raise ValueError(
                "El nombre de la herramienta "
                "no puede estar vacío."
            )

        if not normalized_description:
            raise ValueError(
                "La descripción de la herramienta "
                "no puede estar vacía."
            )

        if not isinstance(
            self.risk_level,
            ToolRiskLevel,
        ):
            raise TypeError(
                "El nivel de riesgo debe ser "
                "un valor de ToolRiskLevel."
            )

        if not isinstance(
            self.requires_confirmation,
            bool,
        ):
            raise TypeError(
                "requires_confirmation debe "
                "ser un valor booleano."
            )

        if not isinstance(
            self.parameters,
            Mapping,
        ):
            raise TypeError(
                "Los parámetros de la herramienta "
                "deben ser un mapping."
            )

        normalized_parameters = dict(
            self.parameters
        )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "description",
            normalized_description,
        )
        object.__setattr__(
            self,
            "parameters",
            MappingProxyType(
                normalized_parameters
            ),
        )