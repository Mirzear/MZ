import unittest

from app.tools.core_tools import CoreTools
from app.tools.tool_call import ToolCall
from app.tools.tool_execution_result import (
    ToolExecutionStatus,
)
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_loader import ToolLoader
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)
from app.tools.tool_registry import ToolRegistry


class TestToolCallExecution(
    unittest.TestCase
):

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

    def test_executes_structured_tool_call(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="count_words",
            arguments={
                "text": (
                    "MZ ejecuta llamadas "
                    "estructuradas"
                ),
            },
        )

        result = (
            self.executor.execute_call(
                tool_call
            )
        )

        self.assertEqual(
            result.status,
            ToolExecutionStatus.SUCCESS,
        )
        self.assertEqual(
            result.output,
            4,
        )
        self.assertEqual(
            result.call_id,
            tool_call.call_id,
        )

    def test_error_preserves_call_id(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="unknown_tool",
            call_id="unknown-call",
        )

        result = (
            self.executor.execute_call(
                tool_call
            )
        )

        self.assertEqual(
            result.status,
            ToolExecutionStatus.ERROR,
        )
        self.assertEqual(
            result.call_id,
            "unknown-call",
        )

    def test_confirmation_result_preserves_call_id(
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

        tool_call = ToolCall(
            tool_name="dangerous_tool"
        )

        result = (
            self.executor.execute_call(
                tool_call
            )
        )

        self.assertEqual(
            result.status,
            ToolExecutionStatus
            .CONFIRMATION_REQUIRED,
        )
        self.assertEqual(
            result.call_id,
            tool_call.call_id,
        )

    def test_executes_confirmed_tool_call(
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

        original_call = ToolCall(
            tool_name="dangerous_tool"
        )

        confirmed_call = (
            original_call.with_confirmation()
        )

        result = (
            self.executor.execute_call(
                confirmed_call
            )
        )

        self.assertEqual(
            result.status,
            ToolExecutionStatus.SUCCESS,
        )
        self.assertEqual(
            result.output,
            "executed",
        )
        self.assertEqual(
            result.call_id,
            original_call.call_id,
        )

    def test_rejects_invalid_tool_call(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            self.executor.execute_call(
                "count_words"
            )


if __name__ == "__main__":
    unittest.main()