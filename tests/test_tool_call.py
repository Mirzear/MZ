import unittest
from types import MappingProxyType

from app.tools.tool_call import ToolCall


class TestToolCall(unittest.TestCase):

    def test_creates_tool_call(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="count_words",
            arguments={
                "text": "uno dos",
            },
        )

        self.assertEqual(
            tool_call.tool_name,
            "count_words",
        )
        self.assertEqual(
            tool_call.arguments["text"],
            "uno dos",
        )
        self.assertFalse(
            tool_call.confirmed
        )
        self.assertTrue(
            tool_call.call_id
        )

    def test_normalizes_tool_name(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="  COUNT_WORDS  "
        )

        self.assertEqual(
            tool_call.tool_name,
            "count_words",
        )

    def test_generates_unique_call_ids(
        self,
    ) -> None:
        first_call = ToolCall(
            tool_name="first"
        )
        second_call = ToolCall(
            tool_name="second"
        )

        self.assertNotEqual(
            first_call.call_id,
            second_call.call_id,
        )

    def test_accepts_custom_call_id(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="count_words",
            call_id="call-123",
        )

        self.assertEqual(
            tool_call.call_id,
            "call-123",
        )

    def test_arguments_are_immutable(
        self,
    ) -> None:
        tool_call = ToolCall(
            tool_name="count_words",
            arguments={
                "text": "uno dos",
            },
        )

        self.assertIsInstance(
            tool_call.arguments,
            MappingProxyType,
        )

        with self.assertRaises(
            TypeError
        ):
            tool_call.arguments[
                "text"
            ] = "modificado"

    def test_rejects_empty_tool_name(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            ToolCall(
                tool_name="   "
            )

    def test_rejects_non_string_tool_name(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            ToolCall(
                tool_name=123
            )

    def test_rejects_invalid_arguments(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            ToolCall(
                tool_name="count_words",
                arguments=[
                    "invalid"
                ],
            )

    def test_rejects_invalid_confirmed_value(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            ToolCall(
                tool_name="count_words",
                confirmed="yes",
            )

    def test_with_confirmation_creates_new_call(
        self,
    ) -> None:
        original_call = ToolCall(
            tool_name="dangerous_tool",
            arguments={
                "value": 10,
            },
        )

        confirmed_call = (
            original_call.with_confirmation()
        )

        self.assertFalse(
            original_call.confirmed
        )
        self.assertTrue(
            confirmed_call.confirmed
        )
        self.assertIsNot(
            original_call,
            confirmed_call,
        )

    def test_with_confirmation_preserves_call_id(
        self,
    ) -> None:
        original_call = ToolCall(
            tool_name="dangerous_tool"
        )

        confirmed_call = (
            original_call.with_confirmation()
        )

        self.assertEqual(
            confirmed_call.call_id,
            original_call.call_id,
        )


if __name__ == "__main__":
    unittest.main()