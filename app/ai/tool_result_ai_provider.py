from typing import Protocol, runtime_checkable

from app.ai.ai_response import AIResponse
from app.tools.tool_execution_result import (
    ToolExecutionResult,
)


@runtime_checkable
class ToolResultAIProvider(Protocol):
    def continue_from_tool_result(
        self,
        *,
        previous_response: AIResponse,
        tool_result: ToolExecutionResult,
    ) -> AIResponse:
        """
        Continue a native provider tool-calling
        turn after executing the requested tool.
        """
        ...