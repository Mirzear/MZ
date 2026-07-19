import unittest
from unittest.mock import Mock

from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)
from app.tools.tool_registry import (
    ToolRegistry,
)


class TestToolRegistry(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = ToolRegistry()

        self.metadata = ToolMetadata(
            name="read_file",
            description=(
                "Lee el contenido "
                "de un archivo."
            ),
            parameters={
                "path": {
                    "type": "string",
                    "required": True,
                },
            },
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

    def test_register_tool(self) -> None:
        self.registry.register(
            self.metadata,
            Mock(),
        )

        self.assertTrue(
            self.registry.exists(
                "read_file"
            )
        )

    def test_get_registered_handler(
        self,
    ) -> None:
        handler = Mock()

        self.registry.register(
            self.metadata,
            handler,
        )

        registered_handler = (
            self.registry.get(
                "read_file"
            )
        )

        self.assertIs(
            registered_handler,
            handler,
        )

    def test_get_unknown_tool_returns_none(
        self,
    ) -> None:
        self.assertIsNone(
            self.registry.get(
                "unknown"
            )
        )

    def test_get_registered_metadata(
        self,
    ) -> None:
        self.registry.register(
            self.metadata,
            Mock(),
        )

        registered_metadata = (
            self.registry.get_metadata(
                "read_file"
            )
        )

        self.assertIs(
            registered_metadata,
            self.metadata,
        )

    def test_get_unknown_metadata_returns_none(
        self,
    ) -> None:
        self.assertIsNone(
            self.registry.get_metadata(
                "unknown"
            )
        )

    def test_tool_name_is_normalized(
        self,
    ) -> None:
        self.registry.register(
            self.metadata,
            Mock(),
        )

        self.assertTrue(
            self.registry.exists(
                "  READ_FILE  "
            )
        )

        self.assertIsNotNone(
            self.registry.get(
                "  READ_FILE  "
            )
        )

    def test_duplicate_tool_raises_error(
        self,
    ) -> None:
        self.registry.register(
            self.metadata,
            Mock(),
        )

        with self.assertRaises(ValueError):
            self.registry.register(
                self.metadata,
                Mock(),
            )

    def test_non_callable_handler_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            self.registry.register(
                self.metadata,
                "not callable",
                # type: ignore[arg-type]
            )

    def test_get_tools_returns_copy(
        self,
    ) -> None:
        self.registry.register(
            self.metadata,
            Mock(),
        )

        tools = self.registry.get_tools()
        tools.add("fake_tool")

        self.assertFalse(
            self.registry.exists(
                "fake_tool"
            )
        )

    def test_get_all_metadata_is_sorted(
        self,
    ) -> None:
        write_metadata = ToolMetadata(
            name="write_file",
            description=(
                "Escribe contenido "
                "en un archivo."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.MEDIUM
            ),
            requires_confirmation=True,
        )

        self.registry.register(
            write_metadata,
            Mock(),
        )
        self.registry.register(
            self.metadata,
            Mock(),
        )

        metadata_collection = (
            self.registry.get_all_metadata()
        )

        self.assertEqual(
            metadata_collection,
            (
                self.metadata,
                write_metadata,
            ),
        )

    def test_count_returns_tool_amount(
        self,
    ) -> None:
        second_metadata = ToolMetadata(
            name="write_file",
            description=(
                "Escribe contenido "
                "en un archivo."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.MEDIUM
            ),
            requires_confirmation=True,
        )

        self.registry.register(
            self.metadata,
            Mock(),
        )
        self.registry.register(
            second_metadata,
            Mock(),
        )

        self.assertEqual(
            self.registry.count(),
            2,
        )


if __name__ == "__main__":
    unittest.main()