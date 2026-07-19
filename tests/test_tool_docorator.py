import unittest

from app.tools.tool_decorator import (
    get_tool_metadata,
    get_tool_name,
    tool,
)
from app.tools.tool_metadata import (
    ToolRiskLevel,
)


class TestToolDecorator(unittest.TestCase):

    def test_tool_stores_name(
        self,
    ) -> None:
        @tool(
            name="read_file",
            description=(
                "Lee el contenido "
                "de un archivo."
            ),
        )
        def handler() -> str:
            return "contenido"

        self.assertEqual(
            get_tool_name(handler),
            "read_file",
        )

    def test_tool_normalizes_name(
        self,
    ) -> None:
        @tool(
            name="  READ_FILE  ",
            description=(
                "Lee un archivo."
            ),
        )
        def handler() -> str:
            return "contenido"

        self.assertEqual(
            get_tool_name(handler),
            "read_file",
        )

    def test_tool_stores_full_metadata(
        self,
    ) -> None:
        parameters = {
            "path": {
                "type": "string",
                "description": (
                    "Ruta del archivo."
                ),
                "required": True,
            },
        }

        @tool(
            name="read_file",
            description=(
                "Lee el contenido "
                "de un archivo."
            ),
            parameters=parameters,
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )
        def handler(
            path: str,
        ) -> str:
            return path

        metadata = get_tool_metadata(
            handler
        )

        self.assertIsNotNone(metadata)

        if metadata is None:
            self.fail(
                "Los metadatos de la "
                "herramienta no fueron "
                "almacenados."
            )

        self.assertEqual(
            metadata.name,
            "read_file",
        )
        self.assertEqual(
            metadata.description,
            (
                "Lee el contenido "
                "de un archivo."
            ),
        )
        self.assertEqual(
            metadata.parameters,
            parameters,
        )
        self.assertEqual(
            metadata.risk_level,
            ToolRiskLevel.LOW,
        )
        self.assertFalse(
            metadata.requires_confirmation
        )

    def test_default_values_are_created(
        self,
    ) -> None:
        @tool(
            name="get_time",
            description=(
                "Obtiene la hora actual."
            ),
        )
        def handler() -> str:
            return "10:30"

        metadata = get_tool_metadata(
            handler
        )

        self.assertIsNotNone(metadata)

        if metadata is None:
            self.fail(
                "Los metadatos de la "
                "herramienta no fueron "
                "almacenados."
            )

        self.assertEqual(
            metadata.parameters,
            {},
        )
        self.assertEqual(
            metadata.risk_level,
            ToolRiskLevel.LOW,
        )
        self.assertFalse(
            metadata.requires_confirmation
        )

    def test_undecorated_function_has_no_name(
        self,
    ) -> None:
        def handler() -> None:
            pass

        self.assertIsNone(
            get_tool_name(handler)
        )

    def test_undecorated_function_has_no_metadata(
        self,
    ) -> None:
        def handler() -> None:
            pass

        self.assertIsNone(
            get_tool_metadata(handler)
        )

    def test_decorator_preserves_function(
        self,
    ) -> None:
        @tool(
            name="add",
            description=(
                "Suma dos números."
            ),
            parameters={
                "first": {
                    "type": "integer",
                    "required": True,
                },
                "second": {
                    "type": "integer",
                    "required": True,
                },
            },
        )
        def add(
            first: int,
            second: int,
        ) -> int:
            return first + second

        self.assertEqual(
            add(2, 3),
            5,
        )

    def test_empty_name_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @tool(
                name="   ",
                description=(
                    "Lee un archivo."
                ),
            )
            def handler() -> None:
                pass

    def test_empty_description_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @tool(
                name="read_file",
                description="   ",
            )
            def handler() -> None:
                pass

    def test_invalid_parameters_raise_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):

            @tool(
                name="read_file",
                description=(
                    "Lee un archivo."
                ),
                parameters=[],
                # type: ignore[arg-type]
            )
            def handler() -> None:
                pass

    def test_invalid_risk_level_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):

            @tool(
                name="read_file",
                description=(
                    "Lee un archivo."
                ),
                risk_level="low",
                # type: ignore[arg-type]
            )
            def handler() -> None:
                pass

    def test_invalid_confirmation_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):

            @tool(
                name="delete_file",
                description=(
                    "Elimina un archivo."
                ),
                requires_confirmation="yes",
                # type: ignore[arg-type]
            )
            def handler() -> None:
                pass


if __name__ == "__main__":
    unittest.main()