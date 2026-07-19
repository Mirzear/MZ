import unittest

from app.commands.command_decorator import (
    command,
    get_command_metadata,
    get_command_name,
)


class TestCommandDecorator(unittest.TestCase):

    def test_command_stores_name(self) -> None:
        @command("hola")
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertEqual(
            get_command_name(handler),
            "hola",
        )

    def test_command_normalizes_name(
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

    def test_command_stores_full_metadata(
        self,
    ) -> None:
        @command(
            name="recordar",
            usage=(
                "recordar "
                "<clave> <valor>"
            ),
            description=(
                "Guarda un dato "
                "en la memoria."
            ),
        )
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        metadata = get_command_metadata(
            handler
        )

        self.assertIsNotNone(metadata)

        if metadata is None:
            self.fail(
                "Los metadatos no fueron "
                "almacenados."
            )

        self.assertEqual(
            metadata.name,
            "recordar",
        )
        self.assertEqual(
            metadata.usage,
            "recordar <clave> <valor>",
        )
        self.assertEqual(
            metadata.description,
            "Guarda un dato en la memoria.",
        )

    def test_default_metadata_is_created(
        self,
    ) -> None:
        @command("hola")
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        metadata = get_command_metadata(
            handler
        )

        self.assertIsNotNone(metadata)

        if metadata is None:
            self.fail(
                "Los metadatos no fueron "
                "almacenados."
            )

        self.assertEqual(
            metadata.usage,
            "hola",
        )
        self.assertEqual(
            metadata.description,
            "Ejecuta el comando 'hola'.",
        )

    def test_undecorated_function_has_no_name(
        self,
    ) -> None:
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertIsNone(
            get_command_name(handler)
        )

    def test_undecorated_function_has_no_metadata(
        self,
    ) -> None:
        def handler(
            _parts: list[str],
        ) -> None:
            pass

        self.assertIsNone(
            get_command_metadata(handler)
        )

    def test_empty_command_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @command("   ")
            def handler(
                _parts: list[str],
            ) -> None:
                pass

    def test_empty_usage_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @command(
                name="hola",
                usage="   ",
                description="Saluda al usuario.",
            )
            def handler(
                _parts: list[str],
            ) -> None:
                pass

    def test_empty_description_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):

            @command(
                name="hola",
                usage="hola",
                description="   ",
            )
            def handler(
                _parts: list[str],
            ) -> None:
                pass


if __name__ == "__main__":
    unittest.main()