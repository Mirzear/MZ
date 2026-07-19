from collections.abc import Iterable
from typing import Any

from google.genai import types

from app.tools.tool_metadata import ToolMetadata


class GeminiToolMapper:
    _SUPPORTED_TYPES = frozenset(
        {
            "string",
            "integer",
            "number",
            "boolean",
            "array",
            "object",
        }
    )

    @classmethod
    def build_tools(
        cls,
        metadata_items: Iterable[ToolMetadata],
    ) -> list[types.Tool]:
        declarations = [
            cls.build_function_declaration(metadata)
            for metadata in metadata_items
        ]

        if not declarations:
            return []

        return [
            types.Tool(
                function_declarations=declarations,
            )
        ]

    @classmethod
    def build_function_declaration(
        cls,
        metadata: ToolMetadata,
    ) -> types.FunctionDeclaration:
        if not isinstance(metadata, ToolMetadata):
            raise TypeError(
                "metadata debe ser una instancia "
                "de ToolMetadata."
            )

        return types.FunctionDeclaration(
            name=metadata.name,
            description=metadata.description,
            parameters_json_schema=(
                cls._build_parameters_schema(
                    metadata.parameters
                )
            ),
        )

    @classmethod
    def _build_parameters_schema(
        cls,
        parameters: Any,
    ) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []

        for parameter_name, parameter_data in (
            parameters.items()
        ):
            if not isinstance(parameter_name, str):
                raise TypeError(
                    "El nombre de cada parámetro "
                    "debe ser una cadena."
                )

            normalized_name = (
                parameter_name.strip()
            )

            if not normalized_name:
                raise ValueError(
                    "El nombre de un parámetro "
                    "no puede estar vacío."
                )

            if not isinstance(parameter_data, dict):
                raise TypeError(
                    f"El parámetro '{normalized_name}' "
                    "debe estar definido mediante "
                    "un diccionario."
                )

            property_schema = (
                cls._build_property_schema(
                    parameter_name=normalized_name,
                    parameter_data=parameter_data,
                )
            )

            properties[normalized_name] = (
                property_schema
            )

            is_required = parameter_data.get(
                "required",
                False,
            )

            if not isinstance(is_required, bool):
                raise TypeError(
                    f"El campo 'required' del parámetro "
                    f"'{normalized_name}' debe ser "
                    "booleano."
                )

            if is_required:
                required.append(normalized_name)

        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    @classmethod
    def _build_property_schema(
        cls,
        *,
        parameter_name: str,
        parameter_data: dict[str, Any],
    ) -> dict[str, Any]:
        parameter_type = parameter_data.get("type")

        if not isinstance(parameter_type, str):
            raise TypeError(
                f"El parámetro '{parameter_name}' "
                "debe declarar un tipo."
            )

        normalized_type = parameter_type.strip().lower()

        if normalized_type not in cls._SUPPORTED_TYPES:
            raise ValueError(
                f"El tipo '{parameter_type}' del "
                f"parámetro '{parameter_name}' "
                "no es compatible con Gemini."
            )

        schema: dict[str, Any] = {
            "type": normalized_type,
        }

        description = parameter_data.get(
            "description"
        )

        if description is not None:
            if not isinstance(description, str):
                raise TypeError(
                    f"La descripción del parámetro "
                    f"'{parameter_name}' debe ser "
                    "una cadena."
                )

            cleaned_description = (
                description.strip()
            )

            if cleaned_description:
                schema["description"] = (
                    cleaned_description
                )

        if normalized_type == "array":
            items = parameter_data.get("items")

            if items is not None:
                if not isinstance(items, dict):
                    raise TypeError(
                        f"El campo 'items' del parámetro "
                        f"'{parameter_name}' debe ser "
                        "un diccionario."
                    )

                schema["items"] = dict(items)

        return schema