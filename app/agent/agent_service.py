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

        if (
            not isinstance(
                max_tool_calls,
                int,
            )
            or isinstance(
                max_tool_calls,
                bool,
            )
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

    @property
    def max_tool_calls(self) -> int:
        return self._max_tool_calls

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
        original_prompt = self._normalize_prompt(
            prompt
        )

        response = self._ai_service.request(
            prompt,
            store_exchange=False,
        )

        if original_prompt is None:
            return response

        if response.is_text:
            self._store_final_response(
                original_prompt=original_prompt,
                response=response,
            )
            return response

        tool_results: list[
            ToolExecutionResult
        ] = []
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
                confirmation_response = (
                    AIResponse.from_text(
                        result.error_message
                        or (
                            "La herramienta requiere "
                            "confirmación."
                        )
                    )
                )

                self._store_final_response(
                    original_prompt=(
                        original_prompt
                    ),
                    response=(
                        confirmation_response
                    ),
                )

                return confirmation_response

            tool_results.append(result)

            agent_prompt = (
                self._build_agent_prompt(
                    original_prompt=(
                        original_prompt
                    ),
                    tool_results=tool_results,
                )
            )

            response = (
                self._ai_service.request(
                    agent_prompt,
                    store_exchange=False,
                )
            )

        if response.is_text:
            self._store_final_response(
                original_prompt=original_prompt,
                response=response,
            )

        return response

    def _store_final_response(
        self,
        *,
        original_prompt: str,
        response: AIResponse,
    ) -> None:
        self._ai_service.record_completed_exchange(
            prompt=original_prompt,
            response=response,
        )

    @classmethod
    def _build_agent_prompt(
        cls,
        *,
        original_prompt: str,
        tool_results: list[
            ToolExecutionResult
        ],
    ) -> str:
        formatted_results = "\n\n".join(
            cls._format_tool_result(
                result=result,
                position=position,
            )
            for position, result in enumerate(
                tool_results,
                start=1,
            )
        )

        return (
            "Consulta original del usuario:\n"
            f"{original_prompt}\n\n"
            "Resultados de herramientas "
            "disponibles:\n"
            f"{formatted_results}\n\n"
            "Usá toda la información anterior "
            "para continuar resolviendo la "
            "consulta original. Podés solicitar "
            "otra herramienta si todavía es "
            "necesaria. Cuando tengas suficiente "
            "información, respondé directamente "
            "al usuario."
        )

    @classmethod
    def _format_tool_result(
        cls,
        *,
        result: ToolExecutionResult,
        position: int,
    ) -> str:
        if result.succeeded:
            result_value = cls._format_value(
                result.output
            )

            return (
                f"Resultado {position}:\n"
                f"- Herramienta: "
                f"{result.tool_name}\n"
                f"- Estado: "
                f"{result.status.value}\n"
                f"- Resultado: "
                f"{result_value}"
            )

        error_message = (
            result.error_message
            or "Error desconocido."
        )

        return (
            f"Resultado {position}:\n"
            f"- Herramienta: "
            f"{result.tool_name}\n"
            f"- Estado: "
            f"{result.status.value}\n"
            f"- Error: {error_message}"
        )

    @staticmethod
    def _format_value(
        value: Any,
    ) -> str:
        if value is None:
            return "None"

        return str(value)

    @staticmethod
    def _normalize_prompt(
        prompt: object,
    ) -> str | None:
        if not isinstance(prompt, str):
            return None

        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            return None

        return cleaned_prompt