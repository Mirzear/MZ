import unittest

from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)


class TestToolMetadata(unittest.TestCase):

    def test_metadata_stores_values(
        self,
    ) -> None:
        parameters = {
            "path": {
                "type": "string",
                "required": True,
            },
        }

        metadata = ToolMetadata(
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

    def test_metadata_normalizes_text(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="  READ_FILE  ",
            description=(
                "  Lee un archivo.  "
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        self.assertEqual(
            metadata.name,
            "read_file",
        )
        self.assertEqual(
            metadata.description,
            "Lee un archivo.",
        )

    def test_empty_name_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ToolMetadata(
                name="   ",
                description=(
                    "Lee un archivo."
                ),
                parameters={},
                risk_level=(
                    ToolRiskLevel.LOW
                ),
                requires_confirmation=False,
            )

    def test_empty_description_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ToolMetadata(
                name="read_file",
                description="   ",
                parameters={},
                risk_level=(
                    ToolRiskLevel.LOW
                ),
                requires_confirmation=False,
            )

    def test_invalid_parameters_raise_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            ToolMetadata(
                name="read_file",
                description=(
                    "Lee un archivo."
                ),
                parameters=[],
                # type: ignore[arg-type]
                risk_level=(
                    ToolRiskLevel.LOW
                ),
                requires_confirmation=False,
            )

    def test_invalid_risk_level_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            ToolMetadata(
                name="read_file",
                description=(
                    "Lee un archivo."
                ),
                parameters={},
                risk_level="low",
                # type: ignore[arg-type]
                requires_confirmation=False,
            )

    def test_invalid_confirmation_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            ToolMetadata(
                name="read_file",
                description=(
                    "Lee un archivo."
                ),
                parameters={},
                risk_level=(
                    ToolRiskLevel.LOW
                ),
                requires_confirmation="no",
                # type: ignore[arg-type]
            )

    def test_parameters_are_copied(
        self,
    ) -> None:
        parameters = {
            "path": {
                "type": "string",
            },
        }

        metadata = ToolMetadata(
            name="read_file",
            description=(
                "Lee un archivo."
            ),
            parameters=parameters,
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        parameters["encoding"] = {
            "type": "string",
        }

        self.assertNotIn(
            "encoding",
            metadata.parameters,
        )

    def test_parameters_cannot_be_replaced(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="read_file",
            description=(
                "Lee un archivo."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        with self.assertRaises(
            AttributeError
        ):
            metadata.parameters = {}
            # type: ignore[misc]

    def test_parameters_cannot_be_modified(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="read_file",
            description=(
                "Lee un archivo."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        with self.assertRaises(TypeError):
            metadata.parameters[
                "path"
            ] = {
                "type": "string",
            }
            # type: ignore[index]


if __name__ == "__main__":
    unittest.main()