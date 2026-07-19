import unittest

from app.commands.command_metadata import (
    CommandMetadata,
)


class TestCommandMetadata(unittest.TestCase):

    def test_metadata_stores_values(
        self,
    ) -> None:
        metadata = CommandMetadata(
            name="hola",
            usage="hola",
            description="Saluda al usuario.",
        )

        self.assertEqual(
            metadata.name,
            "hola",
        )
        self.assertEqual(
            metadata.usage,
            "hola",
        )
        self.assertEqual(
            metadata.description,
            "Saluda al usuario.",
        )

    def test_metadata_normalizes_values(
        self,
    ) -> None:
        metadata = CommandMetadata(
            name="  HOLA  ",
            usage="  hola  ",
            description=(
                "  Saluda al usuario.  "
            ),
        )

        self.assertEqual(
            metadata.name,
            "hola",
        )
        self.assertEqual(
            metadata.usage,
            "hola",
        )
        self.assertEqual(
            metadata.description,
            "Saluda al usuario.",
        )

    def test_empty_name_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            CommandMetadata(
                name="   ",
                usage="hola",
                description=(
                    "Saluda al usuario."
                ),
            )

    def test_empty_usage_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            CommandMetadata(
                name="hola",
                usage="   ",
                description=(
                    "Saluda al usuario."
                ),
            )

    def test_empty_description_raises_error(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            CommandMetadata(
                name="hola",
                usage="hola",
                description="   ",
            )

    def test_metadata_is_immutable(
        self,
    ) -> None:
        metadata = CommandMetadata(
            name="hola",
            usage="hola",
            description="Saluda al usuario.",
        )

        with self.assertRaises(
            AttributeError
        ):
            metadata.name = "otro"
            # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()