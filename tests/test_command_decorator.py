import unittest

from app.commands.command_decorator import (
    command,
    get_command_name,
)


class TestCommandDecorator(unittest.TestCase):

    def test_decorator_stores_command_name(
        self,
    ) -> None:
        @command("hola")
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertEqual(
            get_command_name(handler),
            "hola",
        )

    def test_command_name_is_normalized(
        self,
    ) -> None:
        @command("  HOLA  ")
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertEqual(
            get_command_name(handler),
            "hola",
        )

    def test_function_without_decorator_returns_none(
        self,
    ) -> None:
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertIsNone(
            get_command_name(handler)
        )

    def test_empty_command_name_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @command("   ")
            def handler(
                _parts: list[str],
            ) -> None:
                pass


if __name__ == "__main__":
    unittest.main()