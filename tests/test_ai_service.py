import unittest

from app.ai.ai_response import (
    AIResponse,
    AIResponseType,
)
from app.ai.ai_service import AIService
from app.ai.mock_ai_provider import (
    MockAIProvider,
)
from app.tools.tool_call import ToolCall


class ToolCallProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        return AIResponse.from_tool_call(
            ToolCall(
                tool_name="count_words",
                arguments={
                    "text": prompt,
                },
            )
        )


class ErrorProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        raise RuntimeError(
            "Fallo de prueba"
        )


class InvalidResponseProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        return "respuesta inválida"  # type: ignore


class TestAIService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = AIService(
            provider=MockAIProvider()
        )

    def test_returns_provider_response(
        self,
    ) -> None:
        response = self.service.ask("Hola")

        self.assertEqual(
            response,
            (
                "Respuesta simulada de IA para: "
                "Hola "
                "[contexto previo: 0 mensajes]"
            ),
        )

    def test_removes_prompt_outer_spaces(
        self,
    ) -> None:
        response = self.service.ask(
            "   Hola   "
        )

        self.assertEqual(
            response,
            (
                "Respuesta simulada de IA para: "
                "Hola "
                "[contexto previo: 0 mensajes]"
            ),
        )

    def test_empty_prompt_returns_message(
        self,
    ) -> None:
        response = self.service.ask("   ")

        self.assertEqual(
            response,
            "No recibí ninguna consulta.",
        )

    def test_completed_exchange_is_stored(
        self,
    ) -> None:
        self.service.ask("Hola")

        messages = (
            self.service.get_conversation()
        )

        self.assertEqual(
            len(messages),
            2,
        )

        self.assertEqual(
            messages[0],
            {
                "role": "user",
                "content": "Hola",
            },
        )

        self.assertEqual(
            messages[1]["role"],
            "assistant",
        )

    def test_previous_context_reaches_provider(
        self,
    ) -> None:
        self.service.ask(
            "Primera pregunta"
        )

        response = self.service.ask(
            "Segunda pregunta"
        )

        self.assertIn(
            "[contexto previo: 2 mensajes]",
            response,
        )

    def test_clear_conversation(
        self,
    ) -> None:
        self.service.ask("Hola")

        self.service.clear_conversation()

        self.assertEqual(
            self.service.get_conversation(),
            [],
        )

    def test_request_returns_ai_response(
        self,
    ) -> None:
        response = self.service.request(
            "Hola"
        )

        self.assertIsInstance(
            response,
            AIResponse,
        )
        self.assertEqual(
            response.response_type,
            AIResponseType.TEXT,
        )

    def test_tool_call_is_not_stored_as_completed_exchange(
        self,
    ) -> None:
        service = AIService(
            provider=ToolCallProvider()
        )

        response = service.request(
            "Contá estas palabras"
        )

        self.assertTrue(
            response.is_tool_call
        )
        self.assertEqual(
            service.get_conversation(),
            [],
        )

    def test_provider_exception_returns_error_response(
        self,
    ) -> None:
        service = AIService(
            provider=ErrorProvider()
        )

        response = service.request(
            "Hola"
        )

        self.assertTrue(
            response.is_error
        )
        self.assertEqual(
            response.error_message,
            (
                "No pude obtener una respuesta "
                "de la IA: Fallo de prueba"
            ),
        )

    def test_invalid_provider_response_returns_error(
        self,
    ) -> None:
        service = AIService(
            provider=(
                InvalidResponseProvider()
            )
        )

        response = service.request(
            "Hola"
        )

        self.assertTrue(
            response.is_error
        )
        self.assertEqual(
            response.error_message,
            (
                "El proveedor devolvió una "
                "respuesta inválida."
            ),
        )

    def test_invalid_provider_is_rejected(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            AIService(
                provider=object()
            )


if __name__ == "__main__":
    unittest.main()