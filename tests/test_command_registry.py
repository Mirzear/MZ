import unittest
from unittest.mock import Mock

from app.commands.command_metadata import (
    CommandMetadata,
)
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

    def test_get_registered_handler(
        self,
    ) -> None:
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
            self.registry.get(
                "desconocido"
            )
        )

    def test_command_is_normalized(
        self,
    ) -> None:
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
                "no soy callable",
                # type: ignore[arg-type]
            )

    def test_get_commands_returns_copy(
        self,
    ) -> None:
        self.registry.register(
            "hola",
            Mock(),
        )

        commands = (
            self.registry.get_commands()
        )
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

    def test_register_command_with_metadata(
        self,
    ) -> None:
        handler = Mock()
        metadata = CommandMetadata(
            name="hola",
            usage="hola",
            description="Saluda al usuario.",
        )

        self.registry.register(
            "hola",
            handler,
            metadata,
        )

        registered_metadata = (
            self.registry.get_metadata(
                "hola"
            )
        )

        self.assertIs(
            registered_metadata,
            metadata,
        )

    def test_unknown_command_has_no_metadata(
        self,
    ) -> None:
        self.assertIsNone(
            self.registry.get_metadata(
                "desconocido"
            )
        )

    def test_metadata_name_must_match_command(
        self,
    ) -> None:
        metadata = CommandMetadata(
            name="ayuda",
            usage="ayuda",
            description=(
                "Muestra los comandos."
            ),
        )

        with self.assertRaises(ValueError):
            self.registry.register(
                "hola",
                Mock(),
                metadata,
            )

    def test_get_all_metadata_returns_metadata(
        self,
    ) -> None:
        hola_metadata = CommandMetadata(
            name="hola",
            usage="hola",
            description="Saluda al usuario.",
        )
        ayuda_metadata = CommandMetadata(
            name="ayuda",
            usage="ayuda",
            description=(
                "Muestra los comandos."
            ),
        )

        self.registry.register(
            "hola",
            Mock(),
            hola_metadata,
        )
        self.registry.register(
            "ayuda",
            Mock(),
            ayuda_metadata,
        )

        metadata_collection = (
            self.registry.get_all_metadata()
        )

        self.assertEqual(
            metadata_collection,
            (
                ayuda_metadata,
                hola_metadata,
            ),
        )

    def test_commands_without_metadata_are_excluded(
        self,
    ) -> None:
        self.registry.register(
            "hola",
            Mock(),
        )

        self.assertEqual(
            self.registry.get_all_metadata(),
            (),
        )


if __name__ == "__main__":
    unittest.main()