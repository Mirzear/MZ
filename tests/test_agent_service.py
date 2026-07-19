import unittest

from app.agent.agent_service import AgentService
from app.ai.ai_response import AIResponse
from app.ai.ai_service import AIService
from app.tools.tool_call import ToolCall
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)
from app.tools.tool_registry import ToolRegistry


class SequenceProvider:

    def __init__(
        self,
        responses: list[AIResponse],
    ) -> None:
        self._responses = list(responses)
        self.prompts: list[str] = []

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        self.prompts.append(prompt)

        if not self._responses:
            return AIResponse.from_error(
                "No quedan respuestas simuladas."
            )

        return self._responses.pop(0)


class TestAgentService(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = ToolRegistry()

        self.registry.register(
            metadata=ToolMetadata(
                name="count_words",
                description=(
                    "Cuenta palabras de un texto."
                ),
                parameters={
                    "text": {
                        "type": "string",
                        "required": True,
                    },
                },
                risk_level=ToolRiskLevel.LOW,
                requires_confirmation=False,
            ),
            handler=lambda text: len(
                text.split()
            ),
        )

        self.executor = ToolExecutor(
            registry=self.registry,
        )

    def test_returns_direct_text_response(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_text(
                    "Respuesta directa"
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run("Hola")

        self.assertTrue(response.is_text)

        self.assertEqual(
            response.content,
            "Respuesta directa",
        )

        self.assertEqual(
            provider.prompts,
            ["Hola"],
        )

    def test_executes_tool_and_returns_final_text(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": "uno dos tres",
                        },
                    )
                ),
                AIResponse.from_text(
                    "El texto tiene 3 palabras."
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run(
            "¿Cuántas palabras tiene?"
        )

        self.assertTrue(response.is_text)

        self.assertEqual(
            response.content,
            "El texto tiene 3 palabras.",
        )

        self.assertEqual(
            len(provider.prompts),
            2,
        )

        self.assertIn(
            "Resultado: 3",
            provider.prompts[1],
        )

    def test_supports_multiple_tool_calls(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": "uno dos",
                        },
                    )
                ),
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": (
                                "tres cuatro cinco"
                            ),
                        },
                    )
                ),
                AIResponse.from_text(
                    "Resultados procesados."
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run(
            "Procesá todo"
        )

        self.assertTrue(response.is_text)

        self.assertEqual(
            response.content,
            "Resultados procesados.",
        )

        self.assertEqual(
            len(provider.prompts),
            3,
        )

    def test_sends_tool_error_back_to_ai(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="unknown_tool"
                    )
                ),
                AIResponse.from_text(
                    "No pude usar esa herramienta."
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run(
            "Ejecutá algo"
        )

        self.assertTrue(response.is_text)

        self.assertIn(
            "no está registrada",
            provider.prompts[1],
        )

    def test_returns_confirmation_message_without_recalling_ai(
        self,
    ) -> None:
        self.registry.register(
            metadata=ToolMetadata(
                name="dangerous_tool",
                description=(
                    "Herramienta peligrosa."
                ),
                parameters={},
                risk_level=ToolRiskLevel.HIGH,
                requires_confirmation=True,
            ),
            handler=lambda: "executed",
        )

        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="dangerous_tool"
                    )
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run(
            "Ejecutá la herramienta"
        )

        self.assertTrue(response.is_text)

        self.assertIn(
            "requiere confirmación",
            response.content,
        )

        self.assertEqual(
            len(provider.prompts),
            1,
        )

    def test_stops_after_tool_call_limit(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": "uno",
                        },
                    )
                ),
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": "dos",
                        },
                    )
                ),
            ]
        )

        agent = self._build_agent(
            provider,
            max_tool_calls=1,
        )

        response = agent.run(
            "Entrá en bucle"
        )

        self.assertTrue(response.is_error)

        self.assertIn(
            "superó el límite",
            response.error_message,
        )

        self.assertEqual(
            len(provider.prompts),
            2,
        )

    def test_ask_returns_user_facing_text(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_text("Hola"),
            ]
        )

        agent = self._build_agent(provider)

        result = agent.ask("Hola")

        self.assertEqual(
            result,
            "Hola",
        )

    def test_invalid_ai_service_is_rejected(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            AgentService(
                ai_service=object(),  # type: ignore
                tool_executor=self.executor,
            )

    def test_invalid_tool_executor_is_rejected(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[]
        )

        with self.assertRaises(TypeError):
            AgentService(
                ai_service=AIService(provider),
                tool_executor=object(),  # type: ignore
            )

    def test_invalid_tool_call_limit_is_rejected(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[]
        )

        ai_service = AIService(provider)

        with self.assertRaises(TypeError):
            AgentService(
                ai_service=ai_service,
                tool_executor=self.executor,
                max_tool_calls=True,
            )

        with self.assertRaises(ValueError):
            AgentService(
                ai_service=ai_service,
                tool_executor=self.executor,
                max_tool_calls=0,
            )

    def _build_agent(
        self,
        provider: SequenceProvider,
        max_tool_calls: int = 5,
    ) -> AgentService:
        return AgentService(
            ai_service=AIService(provider),
            tool_executor=self.executor,
            max_tool_calls=max_tool_calls,
        )
    
    def test_accumulates_multiple_tool_results(
        self,
    ) -> None:
        provider = SequenceProvider(
            responses=[
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": "uno dos",
                        },
                    )
                ),
                AIResponse.from_tool_call(
                    ToolCall(
                        tool_name="count_words",
                        arguments={
                            "text": (
                                "tres cuatro cinco"
                            ),
                        },
                    )
                ),
                AIResponse.from_text(
                    "Los resultados son 2 y 3."
                ),
            ]
        )

        agent = self._build_agent(provider)

        response = agent.run(
            "Contá ambos textos"
        )

        self.assertTrue(response.is_text)
        self.assertEqual(
            len(provider.prompts),
            3,
        )

        final_agent_prompt = (
            provider.prompts[2]
        )

        self.assertIn(
            "Consulta original del usuario",
            final_agent_prompt,
        )
        self.assertIn(
            "Contá ambos textos",
            final_agent_prompt,
        )
        self.assertIn(
            "Resultado: 2",
            final_agent_prompt,
        )
        self.assertIn(
            "Resultado: 3",
            final_agent_prompt,
        )


    def test_stores_original_exchange_after_tools(
            self,
        ) -> None:
            provider = SequenceProvider(
                responses=[
                    AIResponse.from_tool_call(
                        ToolCall(
                            tool_name="count_words",
                            arguments={
                                "text": "uno dos tres",
                            },
                        )
                    ),
                    AIResponse.from_text(
                        "El texto tiene 3 palabras."
                    ),
                ]
            )

            ai_service = AIService(provider)

            agent = AgentService(
                ai_service=ai_service,
                tool_executor=self.executor,
            )

            agent.run(
                "¿Cuántas palabras tiene el texto?"
            )

            conversation = (
                ai_service.get_conversation()
            )

            self.assertEqual(
                conversation,
                [
                    {
                        "role": "user",
                        "content": (
                            "¿Cuántas palabras "
                            "tiene el texto?"
                        ),
                    },
                    {
                        "role": "assistant",
                        "content": (
                            "El texto tiene "
                            "3 palabras."
                        ),
                    },
                ],
            )


    def test_does_not_store_internal_agent_prompt(
            self,
        ) -> None:
            provider = SequenceProvider(
                responses=[
                    AIResponse.from_tool_call(
                        ToolCall(
                            tool_name="count_words",
                            arguments={
                                "text": "uno dos",
                            },
                        )
                    ),
                    AIResponse.from_text(
                        "Resultado final"
                    ),
                ]
            )

            ai_service = AIService(provider)

            agent = AgentService(
                ai_service=ai_service,
                tool_executor=self.executor,
            )

            agent.run("Consulta visible")

            conversation_text = str(
                ai_service.get_conversation()
            )

            self.assertNotIn(
                "Resultados de herramientas",
                conversation_text,
            )
            self.assertNotIn(
                "Estado: success",
                conversation_text,
            )


if __name__ == "__main__":
    unittest.main()