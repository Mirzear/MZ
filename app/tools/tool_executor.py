from collections.abc import Mapping
from typing import Any

from app.tools.tool_execution_result import (
    ToolExecutionResult,
    ToolExecutionStatus,
)
from app.tools.tool_metadata import ToolMetadata
from app.tools.tool_registry import ToolRegistry


class ToolExecutor:

    _PARAMETER_TYPES: dict[
        str,
        type | tuple[type, ...],
    ] = {
        "string": str,
        "integer": int,
        "number": (
            int,
            float,
        ),
        "boolean": bool,
        "array": (
            list,
            tuple,
        ),
        "object": Mapping,
    }

    def __init__(
        self,
        registry: ToolRegistry,
    ) -> None:
        if not isinstance(
            registry,
            ToolRegistry,
        ):
            raise TypeError(
                "registry debe ser una "
                "instancia de ToolRegistry."
            )

        self._registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: (
            Mapping[str, Any] | None
        ) = None,
        *,
        confirmed: bool = False,
    ) -> ToolExecutionResult:
        normalized_name = (
            self._normalize_tool_name(
                tool_name
            )
        )

        if normalized_name is None:
            return ToolExecutionResult(
                tool_name="unknown",
                status=(
                    ToolExecutionStatus.ERROR
                ),
                error_message=(
                    "El nombre de la herramienta "
                    "debe ser una cadena no vacía."
                ),
            )

        metadata = (
            self._registry.get_metadata(
                normalized_name
            )
        )

        handler = self._registry.get(
            normalized_name
        )

        if (
            metadata is None
            or handler is None
        ):
            return ToolExecutionResult(
                tool_name=normalized_name,
                status=(
                    ToolExecutionStatus.ERROR
                ),
                error_message=(
                    "La herramienta "
                    f"'{normalized_name}' "
                    "no está registrada."
                ),
            )

        if (
            metadata.requires_confirmation
            and not confirmed
        ):
            return ToolExecutionResult(
                tool_name=normalized_name,
                status=(
                    ToolExecutionStatus
                    .CONFIRMATION_REQUIRED
                ),
                error_message=(
                    "La herramienta "
                    f"'{normalized_name}' "
                    "requiere confirmación."
                ),
            )

        normalized_arguments = (
            self._normalize_arguments(
                arguments
            )
        )

        if normalized_arguments is None:
            return ToolExecutionResult(
                tool_name=normalized_name,
                status=(
                    ToolExecutionStatus.ERROR
                ),
                error_message=(
                    "Los argumentos deben ser "
                    "un mapping."
                ),
            )

        validation_error = (
            self._validate_arguments(
                metadata=metadata,
                arguments=(
                    normalized_arguments
                ),
            )
        )

        if validation_error is not None:
            return ToolExecutionResult(
                tool_name=normalized_name,
                status=(
                    ToolExecutionStatus.ERROR
                ),
                error_message=validation_error,
            )

        try:
            output = handler(
                **normalized_arguments
            )
        except Exception as error:
            return ToolExecutionResult(
                tool_name=normalized_name,
                status=(
                    ToolExecutionStatus.ERROR
                ),
                error_message=(
                    "La herramienta "
                    f"'{normalized_name}' "
                    "produjo un error: "
                    f"{error}"
                ),
            )

        return ToolExecutionResult(
            tool_name=normalized_name,
            status=(
                ToolExecutionStatus.SUCCESS
            ),
            output=output,
        )

    @staticmethod
    def _normalize_tool_name(
        tool_name: Any,
    ) -> str | None:
        if not isinstance(
            tool_name,
            str,
        ):
            return None

        normalized_name = (
            tool_name.strip().lower()
        )

        if not normalized_name:
            return None

        return normalized_name

    @staticmethod
    def _normalize_arguments(
        arguments: (
            Mapping[str, Any] | None
        ),
    ) -> dict[str, Any] | None:
        if arguments is None:
            return {}

        if not isinstance(
            arguments,
            Mapping,
        ):
            return None

        return dict(arguments)

    def _validate_arguments(
        self,
        metadata: ToolMetadata,
        arguments: dict[str, Any],
    ) -> str | None:
        parameter_definitions = (
            metadata.parameters
        )

        unexpected_parameters = (
            set(arguments)
            - set(parameter_definitions)
        )

        if unexpected_parameters:
            parameter_names = ", ".join(
                sorted(
                    unexpected_parameters
                )
            )

            return (
                "La herramienta "
                f"'{metadata.name}' recibió "
                "parámetros inesperados: "
                f"{parameter_names}."
            )

        for (
            parameter_name,
            definition,
        ) in parameter_definitions.items():
            if not isinstance(
                definition,
                Mapping,
            ):
                return (
                    "La definición del parámetro "
                    f"'{parameter_name}' no es "
                    "válida."
                )

            required = definition.get(
                "required",
                False,
            )

            if (
                required
                and parameter_name
                not in arguments
            ):
                return (
                    "Falta el parámetro "
                    f"requerido "
                    f"'{parameter_name}'."
                )

            if parameter_name not in arguments:
                continue

            type_error = (
                self._validate_parameter_type(
                    parameter_name=(
                        parameter_name
                    ),
                    value=arguments[
                        parameter_name
                    ],
                    definition=definition,
                )
            )

            if type_error is not None:
                return type_error

        return None

    def _validate_parameter_type(
        self,
        parameter_name: str,
        value: Any,
        definition: Mapping[str, Any],
    ) -> str | None:
        declared_type = definition.get(
            "type"
        )

        if declared_type is None:
            return None

        if not isinstance(
            declared_type,
            str,
        ):
            return (
                "El tipo declarado para el "
                f"parámetro '{parameter_name}' "
                "no es válido."
            )

        expected_type = (
            self._PARAMETER_TYPES.get(
                declared_type
            )
        )

        if expected_type is None:
            return (
                "El tipo "
                f"'{declared_type}' del "
                f"parámetro '{parameter_name}' "
                "no está soportado."
            )

        if (
            declared_type == "integer"
            and isinstance(value, bool)
        ):
            return (
                "El parámetro "
                f"'{parameter_name}' debe ser "
                "de tipo integer."
            )

        if (
            declared_type == "number"
            and isinstance(value, bool)
        ):
            return (
                "El parámetro "
                f"'{parameter_name}' debe ser "
                "de tipo number."
            )

        if not isinstance(
            value,
            expected_type,
        ):
            return (
                "El parámetro "
                f"'{parameter_name}' debe ser "
                f"de tipo {declared_type}."
            )

        return None