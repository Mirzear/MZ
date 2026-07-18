import unittest
from unittest.mock import Mock

from app.commands.command_registry import (
    CommandRegistry,
)


class TestCommandRegistry(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = CommandRegistry()

    def test_register_command(self) -> None:
        handler = Mock()

        self.registry.register(
            "hola",
            handler,
        )

        self.assertTrue(
            self.registry.exists("hola")
        )

    def test_get_registered_handler(self) -> None:
        handler = Mock()

        self.registry.register(
            "hola",
            handler,
        )

        registered_handler = (
            self.registry.get("hola")
        )

        self.assertIs(
            registered_handler,
            handler,
        )

    def test_get_unknown_command_returns_none(
        self,
    ) -> None:
        self.assertIsNone(
            self.registry.get("desconocido")
        )

    def test_command_is_normalized(self) -> None:
        handler = Mock()

        self.registry.register(
            "  HOLA  ",
            handler,
        )

        self.assertTrue(
            self.registry.exists("hola")
        )

    def test_duplicate_command_raises_error(
        self,
    ) -> None:
        handler = Mock()

        self.registry.register(
            "hola",
            handler,
        )

        with self.assertRaises(ValueError):
            self.registry.register(
                "hola",
                handler,
            )

    def test_empty_command_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            self.registry.register(
                "   ",
                Mock(),
            )

    def test_non_callable_handler_raises_error(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            self.registry.register(
                "hola",
                "no soy callable",  # type: ignore[arg-type]
            )

    def test_get_commands_returns_copy(
        self,
    ) -> None:
        self.registry.register(
            "hola",
            Mock(),
        )

        commands = self.registry.get_commands()
        commands.add("falso")

        self.assertFalse(
            self.registry.exists("falso")
        )

    def test_count_returns_registered_amount(
        self,
    ) -> None:
        self.registry.register(
            "hola",
            Mock(),
        )
        self.registry.register(
            "ayuda",
            Mock(),
        )

        self.assertEqual(
            self.registry.count(),
            2,
        )


if __name__ == "__main__":
    unittest.main()