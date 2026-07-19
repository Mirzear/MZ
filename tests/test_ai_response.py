import unittest

from app.ai.ai_response import (
    AIResponse,
    AIResponseType,
)
from app.tools.tool_call import ToolCall


class TestAIResponse(unittest.TestCase):

    def test_creates_text_response(
        self,
    ) -> None:
        response = AIResponse.from_text(
            "Hola"
        )

        self.assertEqual(
            response.response_type,
            AIResponseType.TEXT,
        )
        self.assertEqual(
            response.content,
            "Hola",
        )

    def test_text_content_is_cleaned(
        self,
    ) -> None:
        response = AIResponse.from_text(
            "   Hola   "
        )

        self.assertEqual(
            response.content,
            "Hola",
        )

    def test_creates_tool_call_response(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="count_words",
        )

        response = (
            AIResponse.from_tool_call(
                tool_call
            )
        )

        self.assertEqual(
            response.response_type,
            AIResponseType.TOOL_CALL,
        )
        self.assertIs(
            response.tool_call,
            tool_call,
        )

    def test_creates_error_response(
        self,
    ) -> None:
        response = AIResponse.from_error(
            "Error de prueba."
        )

        self.assertEqual(
            response.response_type,
            AIResponseType.ERROR,
        )
        self.assertEqual(
            response.error_message,
            "Error de prueba.",
        )

    def test_text_response_properties(
        self,
    ) -> None:
        response = AIResponse.from_text(
            "Hola"
        )

        self.assertTrue(
            response.is_text
        )
        self.assertFalse(
            response.is_tool_call
        )
        self.assertFalse(
            response.is_error
        )
        self.assertTrue(
            response.succeeded
        )

    def test_tool_call_response_properties(
        self,
    ) -> None:
        response = (
            AIResponse.from_tool_call(
                ToolCall(
                    tool_name="count_words"
                )
            )
        )

        self.assertFalse(
            response.is_text
        )
        self.assertTrue(
            response.is_tool_call
        )
        self.assertFalse(
            response.is_error
        )
        self.assertTrue(
            response.succeeded
        )

    def test_error_response_properties(
        self,
    ) -> None:
        response = AIResponse.from_error(
            "Error"
        )

        self.assertFalse(
            response.is_text
        )
        self.assertFalse(
            response.is_tool_call
        )
        self.assertTrue(
            response.is_error
        )
        self.assertFalse(
            response.succeeded
        )

    def test_text_to_user_text(
        self,
    ) -> None:
        response = AIResponse.from_text(
            "Respuesta"
        )

        self.assertEqual(
            response.to_user_text(),
            "Respuesta",
        )

    def test_tool_call_to_user_text(
        self,
    ) -> None:
        response = (
            AIResponse.from_tool_call(
                ToolCall(
                    tool_name="count_words"
                )
            )
        )

        self.assertEqual(
            response.to_user_text(),
            (
                "La IA solicitó ejecutar la "
                "herramienta 'count_words'."
            ),
        )

    def test_error_to_user_text(
        self,
    ) -> None:
        response = AIResponse.from_error(
            "Error de prueba."
        )

        self.assertEqual(
            response.to_user_text(),
            "Error de prueba.",
        )

    def test_rejects_empty_text(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIResponse.from_text("   ")

    def test_rejects_empty_error(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIResponse.from_error("   ")

    def test_tool_response_requires_tool_call(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIResponse(
                response_type=(
                    AIResponseType.TOOL_CALL
                )
            )

    def test_rejects_conflicting_payload(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIResponse(
                response_type=(
                    AIResponseType.TEXT
                ),
                content="Hola",
                error_message="Error",
            )
    def test_tool_call_accepts_provider_state(
        self,
    ) -> None:
        provider_state = object()

        response = AIResponse.from_tool_call(
            ToolCall(
                tool_name="count_words",
                arguments={
                    "text": "Hola mundo",
                },
            ),
            provider_state=provider_state,
        )

        self.assertIs(
            response.provider_state,
            provider_state,
        )


    def test_tool_call_accepts_missing_provider_state(
        self,
    ) -> None:
        response = AIResponse.from_tool_call(
            ToolCall(
                tool_name="count_words",
                arguments={},
            )
        )

        self.assertIsNone(
            response.provider_state
        )


    def test_text_response_rejects_provider_state(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIResponse(
                response_type=AIResponseType.TEXT,
                content="Respuesta",
                provider_state=object(),
            )


    def test_error_response_rejects_provider_state(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIResponse(
                response_type=AIResponseType.ERROR,
                error_message="Error",
                provider_state=object(),
            )


if __name__ == "__main__":
    unittest.main()