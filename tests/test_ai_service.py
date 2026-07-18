import unittest

from app.ai.ai_service import AIService
from app.ai.mock_ai_provider import MockAIProvider


class TestAIService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = AIService(
            provider=MockAIProvider()
        )

    def test_returns_provider_response(self) -> None:
        response = self.service.ask("Hola")

        self.assertEqual(
            response,
            (
                "Respuesta simulada de IA para: Hola "
                "[contexto previo: 0 mensajes]"
            ),
        )

    def test_removes_prompt_outer_spaces(self) -> None:
        response = self.service.ask("   Hola   ")

        self.assertEqual(
            response,
            (
                "Respuesta simulada de IA para: Hola "
                "[contexto previo: 0 mensajes]"
            ),
        )

    def test_empty_prompt_returns_message(self) -> None:
        response = self.service.ask("   ")

        self.assertEqual(
            response,
            "No recibí ninguna consulta.",
        )

    def test_completed_exchange_is_stored(self) -> None:
        self.service.ask("Hola")

        messages = self.service.get_conversation()

        self.assertEqual(len(messages), 2)

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

    def test_previous_context_reaches_provider(self) -> None:
        self.service.ask("Primera pregunta")

        response = self.service.ask(
            "Segunda pregunta"
        )

        self.assertIn(
            "[contexto previo: 2 mensajes]",
            response,
        )

    def test_clear_conversation(self) -> None:
        self.service.ask("Hola")

        self.service.clear_conversation()

        self.assertEqual(
            self.service.get_conversation(),
            [],
        )


if __name__ == "__main__":
    unittest.main()