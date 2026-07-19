import unittest

from app.ai.conversation_manager import (
    ConversationManager,
)
from app.ai.conversation_message import (
    ConversationMessage,
    ConversationRole,
)


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

    def test_accepts_conversation_role(
        self,
    ) -> None:
        self.conversation.add_message(
            role=ConversationRole.ASSISTANT,
            content="Hola",
        )

        message = (
            self.conversation
            .get_message_objects()[0]
        )

        self.assertIs(
            message.role,
            ConversationRole.ASSISTANT,
        )

    def test_accepts_all_supported_roles(
        self,
    ) -> None:
        conversation = ConversationManager(
            max_messages=4
        )

        for role in ConversationRole:
            conversation.add_message(
                role=role,
                content=f"Mensaje {role.value}",
            )

        self.assertEqual(
            conversation.count(),
            4,
        )

        self.assertEqual(
            conversation.VALID_ROLES,
            {
                "system",
                "user",
                "assistant",
                "tool",
            },
        )

    def test_adds_message_object(self) -> None:
        message = ConversationMessage(
            role=ConversationRole.TOOL,
            content="Resultado",
        )

        self.conversation.add(message)

        self.assertEqual(
            self.conversation
            .get_message_objects(),
            [message],
        )

    def test_rejects_invalid_message_object(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            self.conversation.add(
                object()  # type: ignore[arg-type]
            )

    def test_content_is_cleaned(self) -> None:
        self.conversation.add_message(
            role="user",
            content=" Hola ",
        )

        self.assertEqual(
            self.conversation
            .get_messages()[0]["content"],
            "Hola",
        )

    def test_invalid_role_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            self.conversation.add_message(
                role="invalid",
                content="Mensaje",
            )

    def test_empty_content_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            self.conversation.add_message(
                role="user",
                content=" ",
            )

    def test_message_limit_is_respected(
        self,
    ) -> None:
        self.conversation.add_message(
            "user",
            "Uno",
        )
        self.conversation.add_message(
            "assistant",
            "Dos",
        )
        self.conversation.add_message(
            "user",
            "Tres",
        )
        self.conversation.add_message(
            "assistant",
            "Cuatro",
        )

        messages = (
            self.conversation.get_messages()
        )

        self.assertEqual(
            len(messages),
            3,
        )
        self.assertEqual(
            messages[0]["content"],
            "Dos",
        )

    def test_get_messages_returns_copy(
        self,
    ) -> None:
        self.conversation.add_message(
            "user",
            "Hola",
        )

        messages = (
            self.conversation.get_messages()
        )
        messages[0]["content"] = "Modificado"

        self.assertEqual(
            self.conversation
            .get_messages()[0]["content"],
            "Hola",
        )

    def test_get_message_objects_returns_copy(
        self,
    ) -> None:
        self.conversation.add_message(
            "user",
            "Hola",
        )

        messages = (
            self.conversation
            .get_message_objects()
        )
        messages.clear()

        self.assertEqual(
            self.conversation.count(),
            1,
        )

    def test_messages_property_returns_copy(
        self,
    ) -> None:
        self.conversation.add_message(
            "user",
            "Hola",
        )

        messages = self.conversation.messages
        messages.clear()

        self.assertEqual(
            self.conversation.count(),
            1,
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

    def test_count(self) -> None:
        self.assertEqual(
            self.conversation.count(),
            0,
        )

        self.conversation.add_message(
            "user",
            "Hola",
        )

        self.assertEqual(
            self.conversation.count(),
            1,
        )

    def test_invalid_max_messages_type(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            ConversationManager(
                max_messages="20"  # type: ignore[arg-type]
            )

        with self.assertRaises(TypeError):
            ConversationManager(
                max_messages=True
            )

    def test_invalid_max_messages_value(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ConversationManager(
                max_messages=0
            )


if __name__ == "__main__":
    unittest.main()