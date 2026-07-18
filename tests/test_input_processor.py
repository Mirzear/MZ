import unittest

from app.core.input_processor import InputProcessor


class TestInputProcessor(unittest.TestCase):

    def setUp(self) -> None:
        self.processor = InputProcessor()

    def test_normalize_removes_extra_spaces(self) -> None:
        result = self.processor.normalize(
            "   recordar     ciudad     Buenos Aires   "
        )

        self.assertEqual(
            result,
            "recordar ciudad Buenos Aires",
        )

    def test_split_preserves_value_spaces(self) -> None:
        result = self.processor.split(
            "recordar comida milanesa con puré"
        )

        self.assertEqual(
            result,
            [
                "recordar",
                "comida",
                "milanesa con puré",
            ],
        )

    def test_alias_is_converted_to_official_command(self) -> None:
        parts = self.processor.split("guardar color azul")
        command = self.processor.get_command(parts)

        self.assertEqual(command, "recordar")

    def test_command_is_converted_to_lowercase(self) -> None:
        parts = self.processor.split("CONSULTAR ciudad")
        command = self.processor.get_command(parts)

        self.assertEqual(command, "consultar")

    def test_empty_input_returns_empty_command(self) -> None:
        parts = self.processor.split("      ")
        command = self.processor.get_command(parts)

        self.assertEqual(parts, [])
        self.assertEqual(command, "")

    def test_suggests_similar_command(self) -> None:
        suggestion = self.processor.suggest_command("colsultar")

        self.assertEqual(suggestion, "consultar")

    def test_unrelated_word_has_no_suggestion(self) -> None:
        suggestion = self.processor.suggest_command("banana")

        self.assertIsNone(suggestion)


if __name__ == "__main__":
    unittest.main()