import unittest

from app.ai.ai_response import (
    AIResponse,
    AIResponseType,
)
from app.ai.mock_ai_provider import (
    MockAIProvider,
)


class TestMockAIProvider(unittest.TestCase):

    def setUp(self) -> None:
        self.provider = MockAIProvider()

    def test_returns_structured_response(
        self,
    ) -> None:
        response = (
            self.provider.generate_response(
                prompt="Hola",
                context=[],
            )
        )

        self.assertIsInstance(
            response,
            AIResponse,
        )
        self.assertEqual(
            response.response_type,
            AIResponseType.TEXT,
        )

    def test_reports_context_length(
        self,
    ) -> None:
        context = [
            {
                "role": "user",
                "content": "Primera pregunta",
            },
            {
                "role": "assistant",
                "content": "Primera respuesta",
            },
        ]

        response = (
            self.provider.generate_response(
                prompt="Segunda pregunta",
                context=context,
            )
        )

        self.assertEqual(
            response.content,
            (
                "Respuesta simulada de IA para: "
                "Segunda pregunta "
                "[contexto previo: 2 mensajes]"
            ),
        )


if __name__ == "__main__":
    unittest.main()