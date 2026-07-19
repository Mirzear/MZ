import unittest

from app.ai.conversation_message import (
    ConversationMessage,
    ConversationRole,
)


class TestConversationRole(unittest.TestCase):

    def test_accepts_enum_value(self) -> None:
        role = ConversationRole.from_value(
            ConversationRole.USER
        )

        self.assertIs(
            role,
            ConversationRole.USER,
        )

    def test_normalizes_string_value(self) -> None:
        role = ConversationRole.from_value(
            " Assistant "
        )

        self.assertIs(
            role,
            ConversationRole.ASSISTANT,
        )

    def test_rejects_invalid_role(self) -> None:
        with self.assertRaises(ValueError):
            ConversationRole.from_value(
                "invalid"
            )

    def test_rejects_non_string_role(self) -> None:
        with self.assertRaises(TypeError):
            ConversationRole.from_value(
                10  # type: ignore[arg-type]
            )


class TestConversationMessage(unittest.TestCase):

    def test_creates_message(self) -> None:
        message = ConversationMessage(
            role=ConversationRole.USER,
            content="Hola",
        )

        self.assertIs(
            message.role,
            ConversationRole.USER,
        )
        self.assertEqual(
            message.content,
            "Hola",
        )

    def test_accepts_string_role(self) -> None:
        message = ConversationMessage(
            role="assistant",  # type: ignore[arg-type]
            content="Respuesta",
        )

        self.assertIs(
            message.role,
            ConversationRole.ASSISTANT,
        )

    def test_cleans_content(self) -> None:
        message = ConversationMessage(
            role=ConversationRole.USER,
            content=" Hola ",
        )

        self.assertEqual(
            message.content,
            "Hola",
        )

    def test_supports_all_roles(self) -> None:
        for role in ConversationRole:
            message = ConversationMessage(
                role=role,
                content="Mensaje",
            )

            self.assertIs(
                message.role,
                role,
            )

    def test_rejects_empty_content(self) -> None:
        with self.assertRaises(ValueError):
            ConversationMessage(
                role=ConversationRole.USER,
                content=" ",
            )

    def test_rejects_non_string_content(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            ConversationMessage(
                role=ConversationRole.USER,
                content=10,  # type: ignore[arg-type]
            )

    def test_is_immutable(self) -> None:
        message = ConversationMessage(
            role=ConversationRole.USER,
            content="Hola",
        )

        with self.assertRaises(
            AttributeError
        ):
            message.content = (  # type: ignore[misc]
                "Modificado"
            )

    def test_converts_to_dictionary(self) -> None:
        message = ConversationMessage(
            role=ConversationRole.TOOL,
            content="Resultado",
        )

        self.assertEqual(
            message.to_dict(),
            {
                "role": "tool",
                "content": "Resultado",
            },
        )

    def test_creates_from_dictionary(
        self,
    ) -> None:
        message = (
            ConversationMessage.from_dict(
                {
                    "role": "system",
                    "content": "Instrucción",
                }
            )
        )

        self.assertIs(
            message.role,
            ConversationRole.SYSTEM,
        )
        self.assertEqual(
            message.content,
            "Instrucción",
        )

    def test_from_dictionary_requires_role(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ConversationMessage.from_dict(
                {
                    "content": "Mensaje",
                }
            )

    def test_from_dictionary_requires_content(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            ConversationMessage.from_dict(
                {
                    "role": "user",
                }
            )


if __name__ == "__main__":
    unittest.main()