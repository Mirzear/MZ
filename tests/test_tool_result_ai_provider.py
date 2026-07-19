import unittest

from app.ai.ai_response import AIResponse
from app.ai.tool_result_ai_provider import (
    ToolResultAIProvider,
)
from app.tools.tool_call import ToolCall
from app.tools.tool_execution_result import (
    ToolExecutionResult,
    ToolExecutionStatus,
)


class CompatibleProvider:
    def continue_from_tool_result(
        self,
        *,
        previous_response: AIResponse,
        tool_result: ToolExecutionResult,
    ) -> AIResponse:
        return AIResponse.from_text(
            "Continuación completa"
        )


class IncompatibleProvider:
    pass


class TestToolResultAIProvider(
    unittest.TestCase
):
    def test_detects_compatible_provider(
        self,
    ) -> None:
        provider = CompatibleProvider()

        self.assertIsInstance(
            provider,
            ToolResultAIProvider,
        )

    def test_rejects_incompatible_provider(
        self,
    ) -> None:
        provider = IncompatibleProvider()

        self.assertNotIsInstance(
            provider,
            ToolResultAIProvider,
        )

    def test_compatible_provider_can_continue(
        self,
    ) -> None:
        provider = CompatibleProvider()

        previous_response = (
            AIResponse.from_tool_call(
                ToolCall(
                    tool_name="count_words",
                    arguments={
                        "text": "uno dos",
                    },
                )
            )
        )

        tool_result = ToolExecutionResult(
            tool_name="count_words",
            status=(
                ToolExecutionStatus.SUCCESS
            ),
            output=2,
            call_id=(
                previous_response
                .tool_call
                .call_id
            ),
        )

        response = (
            provider.continue_from_tool_result(
                previous_response=(
                    previous_response
                ),
                tool_result=tool_result,
            )
        )

        self.assertTrue(response.is_text)
        self.assertEqual(
            response.content,
            "Continuación completa",
        )


if __name__ == "__main__":
    unittest.main()