from typing import Any

from app.ai.ai_response import AIResponse
from app.ai.ai_service import AIService
from app.tools.tool_execution_result import (
    ToolExecutionResult,
)
from app.tools.tool_executor import ToolExecutor


class AgentService:

    def __init__(
        self,
        ai_service: AIService,
        tool_executor: ToolExecutor,
        max_tool_calls: int = 5,
    ) -> None:
        if not isinstance(
            ai_service,
            AIService,
        ):
            raise TypeError(
                "ai_service debe ser una "
                "instancia de AIService."
            )

        if not isinstance(
            tool_executor,
            ToolExecutor,
        ):
            raise TypeError(
                "tool_executor debe ser una "
                "instancia de ToolExecutor."
            )

        if not isinstance(
            max_tool_calls,
            int,
        ) or isinstance(
            max_tool_calls,
            bool,
        ):
            raise TypeError(
                "max_tool_calls debe ser un "
                "número entero."
            )

        if max_tool_calls < 1:
            raise ValueError(
                "max_tool_calls debe ser mayor "
                "o igual que 1."
            )

        self._ai_service = ai_service
        self._tool_executor = tool_executor
        self._max_tool_calls = max_tool_calls

    def ask(
        self,
        prompt: str,
    ) -> str:
        response = self.run(prompt)

        return response.to_user_text()

    def run(
        self,
        prompt: str,
    ) -> AIResponse:
        response = self._ai_service.request(
            prompt
        )

        executed_tool_calls = 0

        while response.is_tool_call:
            if (
                executed_tool_calls
                >= self._max_tool_calls
            ):
                return AIResponse.from_error(
                    "La IA superó el límite de "
                    "ejecuciones de herramientas "
                    "permitidas para una consulta."
                )

            tool_call = response.tool_call

            if tool_call is None:
                return AIResponse.from_error(
                    "La IA solicitó una "
                    "herramienta inválida."
                )

            result = (
                self._tool_executor.execute_call(
                    tool_call
                )
            )

            executed_tool_calls += 1

            if result.requires_confirmation:
                return AIResponse.from_text(
                    result.error_message
                    or (
                        "La herramienta requiere "
                        "confirmación."
                    )
                )

            response = self._ai_service.request(
                self._build_tool_result_prompt(
                    result
                )
            )

        return response

    @staticmethod
    def _build_tool_result_prompt(
        result: ToolExecutionResult,
    ) -> str:
        if result.succeeded:
            result_value = (
                AgentService._format_value(
                    result.output
                )
            )

            return (
                "Resultado de la herramienta "
                f"'{result.tool_name}':\n"
                f"Estado: {result.status.value}\n"
                f"Resultado: {result_value}\n"
                "Usá este resultado para responder "
                "la consulta original del usuario."
            )

        error_message = (
            result.error_message
            or "Error desconocido."
        )

        return (
            "La ejecución de la herramienta "
            f"'{result.tool_name}' falló:\n"
            f"Estado: {result.status.value}\n"
            f"Error: {error_message}\n"
            "Explicá el problema al usuario o "
            "elegí otra acción válida."
        )

    @staticmethod
    def _format_value(
        value: Any,
    ) -> str:
        if value is None:
            return "None"

        return str(value)