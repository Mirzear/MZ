import unittest

from app.commands.command_registry import (
    CommandRegistry,
)
from app.core.input_processor import InputProcessor


class TestInputProcessor(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = CommandRegistry()

        self.registry.register(
            "hola",
            lambda _parts: None,
        )
        self.registry.register(
            "ayuda",
            lambda _parts: None,
        )
        self.registry.register(
            "salir",
            lambda _parts: None,
        )
        self.registry.register(
            "recordar",
            lambda _parts: None,
        )
        self.registry.register(
            "consultar",
            lambda _parts: None,
        )
        self.registry.register(
            "olvidar",
            lambda _parts: None,
        )
        self.registry.register(
            "memorias",
            lambda _parts: None,
        )
        self.registry.register(
            "preguntar",
            lambda _parts: None,
        )
        self.registry.register(
            "conversacion",
            lambda _parts: None,
        )
        self.registry.register(
            "borrar_conversacion",
            lambda _parts: None,
        )

        self.processor = InputProcessor(
            registry=self.registry,
        )

    def test_normalize_removes_extra_spaces(
        self,
    ) -> None:
        result = self.processor.normalize(
            "   recordar    lenguaje    Python   "
        )

        self.assertEqual(
            result,
            "recordar lenguaje Python",
        )

    def test_split_preserves_value_spaces(
        self,
    ) -> None:
        result = self.processor.split(
            "recordar lenguaje Python es dinámico"
        )

        self.assertEqual(
            result,
            [
                "recordar",
                "lenguaje",
                "Python es dinámico",
            ],
        )

    def test_empty_input_returns_empty_command(
        self,
    ) -> None:
        result = self.processor.get_command([])

        self.assertEqual(
            result,
            "",
        )

    def test_command_is_converted_to_lowercase(
        self,
    ) -> None:
        result = self.processor.get_command(
            ["HOLA"]
        )

        self.assertEqual(
            result,
            "hola",
        )

    def test_alias_is_converted_to_official_command(
        self,
    ) -> None:
        result = self.processor.get_command(
            ["guardar"]
        )

        self.assertEqual(
            result,
            "recordar",
        )

    def test_suggests_similar_command(
        self,
    ) -> None:
        result = self.processor.suggest_command(
            "colsultar"
        )

        self.assertEqual(
            result,
            "consultar",
        )

    def test_unrelated_word_has_no_suggestion(
        self,
    ) -> None:
        result = self.processor.suggest_command(
            "xyzabc"
        )

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()