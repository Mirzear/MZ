import unittest
from contextlib import redirect_stdout
from io import StringIO

from app.core.mz import MZ
from app.tools.tool_execution_result import (
    ToolExecutionStatus,
)


class TestMZToolIntegration(
    unittest.TestCase
):

    def setUp(self) -> None:
        self.mz = MZ()

    def test_core_tools_are_registered(
        self,
    ) -> None:
        self.assertTrue(
            self.mz.tool_registry.exists(
                "count_words"
            )
        )
        self.assertTrue(
            self.mz.tool_registry.exists(
                "get_current_datetime"
            )
        )
        self.assertEqual(
            self.mz.tool_registry.count(),
            2,
        )

    def test_registered_count_words_handler(
        self,
    ) -> None:
        handler = self.mz.tool_registry.get(
            "count_words"
        )

        self.assertIsNotNone(handler)

        if handler is None:
            self.fail(
                "La herramienta count_words "
                "no fue registrada."
            )

        result = handler(
            "MZ utiliza sus herramientas"
        )

        self.assertEqual(
            result,
            4,
        )

    def test_tools_command_is_registered(
        self,
    ) -> None:
        self.assertTrue(
            self.mz.command_registry.exists(
                "herramientas"
            )
        )

    def test_tools_command_shows_registered_tools(
        self,
    ) -> None:
        output = StringIO()

        with redirect_stdout(output):
            self.mz.command_processor.process(
                "herramientas"
            )

        result = output.getvalue()

        self.assertIn(
            "Herramientas disponibles",
            result,
        )
        self.assertIn(
            "count_words",
            result,
        )
        self.assertIn(
            "get_current_datetime",
            result,
        )
        self.assertIn(
            "Riesgo: low",
            result,
        )

    def test_mz_has_tool_executor(
        self,
    ) -> None:
        self.assertIsNotNone(
            self.mz.tool_executor
        )

    def test_mz_executor_runs_core_tool(
        self,
    ) -> None:
        result = (
            self.mz.tool_executor.execute(
                "count_words",
                {
                    "text": (
                        "MZ tiene un ejecutor"
                    ),
                },
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


if __name__ == "__main__":
    unittest.main()