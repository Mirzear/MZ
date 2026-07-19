import unittest

from app.ai.ai_response import AIResponse
from app.ai.ai_stream_event import (
    AIStreamEvent,
    AIStreamEventType,
)
from app.tools.tool_call import ToolCall


class TestAIStreamEvent(unittest.TestCase):

    def test_creates_text_delta_event(
        self,
    ) -> None:
        event = AIStreamEvent.from_text_delta(
            "Hola"
        )

        self.assertEqual(
            event.event_type,
            AIStreamEventType.TEXT_DELTA,
        )
        self.assertEqual(
            event.text_delta,
            "Hola",
        )
        self.assertIsNone(event.response)
        self.assertTrue(event.is_text_delta)
        self.assertFalse(event.is_completed)

    def test_preserves_delta_whitespace(
        self,
    ) -> None:
        event = AIStreamEvent.from_text_delta(
            " mundo"
        )

        self.assertEqual(
            event.text_delta,
            " mundo",
        )

    def test_creates_completed_text_event(
        self,
    ) -> None:
        response = AIResponse.from_text(
            "Respuesta completa"
        )

        event = (
            AIStreamEvent
            .from_completed_response(
                response
            )
        )

        self.assertEqual(
            event.event_type,
            AIStreamEventType.COMPLETED,
        )
        self.assertIs(
            event.response,
            response,
        )
        self.assertIsNone(event.text_delta)
        self.assertTrue(event.is_completed)
        self.assertFalse(event.is_text_delta)

    def test_creates_completed_tool_call_event(
        self,
    ) -> None:
        response = AIResponse.from_tool_call(
            ToolCall(
                tool_name="count_words",
                arguments={
                    "text": "Hola mundo",
                },
            )
        )

        event = (
            AIStreamEvent
            .from_completed_response(
                response
            )
        )

        self.assertTrue(event.is_completed)
        self.assertIs(
            event.response,
            response,
        )
        self.assertTrue(
            event.response.is_tool_call
        )

    def test_rejects_empty_text_delta(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIStreamEvent.from_text_delta("")

    def test_rejects_invalid_event_type(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            AIStreamEvent(
                event_type=(
                    "text_delta"  # type: ignore[arg-type]
                ),
                text_delta="Hola",
            )

    def test_text_delta_requires_text(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIStreamEvent(
                event_type=(
                    AIStreamEventType.TEXT_DELTA
                )
            )

    def test_text_delta_rejects_response(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIStreamEvent(
                event_type=(
                    AIStreamEventType.TEXT_DELTA
                ),
                text_delta="Hola",
                response=AIResponse.from_text(
                    "Respuesta"
                ),
            )

    def test_completed_event_requires_response(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIStreamEvent(
                event_type=(
                    AIStreamEventType.COMPLETED
                )
            )

    def test_completed_event_rejects_delta(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AIStreamEvent(
                event_type=(
                    AIStreamEventType.COMPLETED
                ),
                text_delta="Hola",
                response=AIResponse.from_text(
                    "Hola"
                ),
            )

    def test_rejects_invalid_response(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            AIStreamEvent(
                event_type=(
                    AIStreamEventType.COMPLETED
                ),
                response=(
                    object()  # type: ignore[arg-type]
                ),
            )


if __name__ == "__main__":
    unittest.main()