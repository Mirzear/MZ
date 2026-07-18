import unittest

from app.ai.conversation_manager import ConversationManager


class TestConversationManager(unittest.TestCase):

    def setUp(self) -> None:
        self.conversation = ConversationManager(
            max_messages=3
        )

    def test_add_message(self) -> None:
        self.conversation.add_message(
            role="user",
            content="Hola",
        )

        self.assertEqual(
            self.conversation.get_messages(),
            [
                {
                    "role": "user",
                    "content": "Hola",
                }
            ],
        )

    def test_content_is_cleaned(self) -> None:
        self.conversation.add_message(
            role="user",
            content="   Hola   ",
        )

        self.assertEqual(
            self.conversation.get_messages()[0][
                "content"
            ],
            "Hola",
        )

    def test_invalid_role_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.conversation.add_message(
                role="system",
                content="Mensaje",
            )

    def test_empty_content_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.conversation.add_message(
                role="user",
                content="   ",
            )

    def test_message_limit_is_respected(self) -> None:
        self.conversation.add_message("user", "Uno")
        self.conversation.add_message(
            "assistant",
            "Dos",
        )
        self.conversation.add_message("user", "Tres")
        self.conversation.add_message(
            "assistant",
            "Cuatro",
        )

        messages = self.conversation.get_messages()

        self.assertEqual(len(messages), 3)
        self.assertEqual(
            messages[0]["content"],
            "Dos",
        )

    def test_get_messages_returns_copy(self) -> None:
        self.conversation.add_message(
            "user",
            "Hola",
        )

        messages = self.conversation.get_messages()
        messages[0]["content"] = "Modificado"

        self.assertEqual(
            self.conversation.get_messages()[0][
                "content"
            ],
            "Hola",
        )

    def test_clear(self) -> None:
        self.conversation.add_message(
            "user",
            "Hola",
        )

        self.conversation.clear()

        self.assertEqual(
            self.conversation.get_messages(),
            [],
        )

    def test_invalid_max_messages_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ConversationManager(max_messages=0)


if __name__ == "__main__":
    unittest.main()