import unittest

from app.tools.core_tools import CoreTools
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_execution_result import (
    ToolExecutionStatus,
)
from app.tools.tool_loader import ToolLoader
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)
from app.tools.tool_registry import ToolRegistry


class TestToolExecutor(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = ToolRegistry()

        loader = ToolLoader(
            registry=self.registry,
        )

        loader.load(
            CoreTools()
        )

        self.executor = ToolExecutor(
            registry=self.registry,
        )

    def test_executes_tool_without_arguments(
        self,
    ) -> None:
        result = self.executor.execute(
            "get_current_datetime"
        )

        self.assertTrue(
            result.succeeded
        )
        self.assertEqual(
            result.status,
            ToolExecutionStatus.SUCCESS,
        )
        self.assertIsInstance(
            result.output,
            str,
        )
        self.assertIsNone(
            result.error_message
        )

    def test_executes_tool_with_arguments(
        self,
    ) -> None:
        result = self.executor.execute(
            "count_words",
            {
                "text": (
                    "MZ ejecuta herramientas"
                ),
            },
        )

        self.assertTrue(
            result.succeeded
        )
        self.assertEqual(
            result.output,
            3,
        )

    def test_normalizes_tool_name(
        self,
    ) -> None:
        result = self.executor.execute(
            "  COUNT_WORDS  ",
            {
                "text": "uno dos",
            },
        )

        self.assertTrue(
            result.succeeded
        )
        self.assertEqual(
            result.tool_name,
            "count_words",
        )

    def test_returns_error_for_unknown_tool(
        self,
    ) -> None:
        result = self.executor.execute(
            "unknown_tool"
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertEqual(
            result.status,
            ToolExecutionStatus.ERROR,
        )
        self.assertIn(
            "no está registrada",
            result.error_message,
        )

    def test_returns_error_for_empty_name(
        self,
    ) -> None:
        result = self.executor.execute(
            "   "
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertIn(
            "nombre de la herramienta",
            result.error_message,
        )

    def test_returns_error_for_missing_argument(
        self,
    ) -> None:
        result = self.executor.execute(
            "count_words"
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertIn(
            "Falta el parámetro requerido",
            result.error_message,
        )
        self.assertIn(
            "text",
            result.error_message,
        )

    def test_returns_error_for_unexpected_argument(
        self,
    ) -> None:
        result = self.executor.execute(
            "count_words",
            {
                "text": "uno dos",
                "extra": True,
            },
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertIn(
            "parámetros inesperados",
            result.error_message,
        )
        self.assertIn(
            "extra",
            result.error_message,
        )

    def test_returns_error_for_invalid_type(
        self,
    ) -> None:
        result = self.executor.execute(
            "count_words",
            {
                "text": 123,
            },
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertIn(
            "debe ser de tipo string",
            result.error_message,
        )

    def test_blocks_tool_requiring_confirmation(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="dangerous_tool",
            description=(
                "Herramienta de prueba."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.HIGH
            ),
            requires_confirmation=True,
        )

        self.registry.register(
            metadata=metadata,
            handler=lambda: "executed",
        )

        result = self.executor.execute(
            "dangerous_tool"
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertTrue(
            result.requires_confirmation
        )
        self.assertEqual(
            result.status,
            ToolExecutionStatus
            .CONFIRMATION_REQUIRED,
        )

    def test_executes_confirmed_tool(
        self,
    ) -> None:
        metadata = ToolMetadata(
            name="dangerous_tool",
            description=(
                "Herramienta de prueba."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.HIGH
            ),
            requires_confirmation=True,
        )

        self.registry.register(
            metadata=metadata,
            handler=lambda: "executed",
        )

        result = self.executor.execute(
            "dangerous_tool",
            confirmed=True,
        )

        self.assertTrue(
            result.succeeded
        )
        self.assertEqual(
            result.output,
            "executed",
        )

    def test_captures_handler_exception(
        self,
    ) -> None:
        def failing_handler() -> None:
            raise RuntimeError(
                "fallo controlado"
            )

        metadata = ToolMetadata(
            name="failing_tool",
            description=(
                "Herramienta que falla."
            ),
            parameters={},
            risk_level=(
                ToolRiskLevel.LOW
            ),
            requires_confirmation=False,
        )

        self.registry.register(
            metadata=metadata,
            handler=failing_handler,
        )

        result = self.executor.execute(
            "failing_tool"
        )

        self.assertFalse(
            result.succeeded
        )
        self.assertIn(
            "produjo un error",
            result.error_message,
        )
        self.assertIn(
            "fallo controlado",
            result.error_message,
        )


if __name__ == "__main__":
    unittest.main()