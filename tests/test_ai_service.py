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
            "Respuesta simulada de IA para: Hola",
        )

    def test_removes_prompt_outer_spaces(self) -> None:
        response = self.service.ask("   Hola   ")

        self.assertEqual(
            response,
            "Respuesta simulada de IA para: Hola",
        )

    def test_empty_prompt_returns_message(self) -> None:
        response = self.service.ask("   ")

        self.assertEqual(
            response,
            "No recibí ninguna consulta.",
        )


if __name__ == "__main__":
    unittest.main()