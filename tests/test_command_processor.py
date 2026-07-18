import unittest
from unittest.mock import Mock

from app.commands.command_processor import (
    CommandProcessor,
)
from app.commands.command_registry import (
    CommandRegistry,
)


class TestCommandProcessor(unittest.TestCase):

    def setUp(self) -> None:
        self.mz = Mock()
        self.registry = CommandRegistry()

        self.mz.name = "MZ"

        self.mz.input_processor.split.side_effect = (
            lambda text: text.split()
        )

        self.mz.input_processor.get_command.side_effect = (
            lambda parts: parts[0]
        )

        self.mz.input_processor.suggest_command.return_value = (
            None
        )

        self.processor = CommandProcessor(
            mz=self.mz,
            registry=self.registry,
        )

    def test_known_command_executes_handler(
        self,
    ) -> None:
        handler = Mock()

        self.registry.register(
            "prueba",
            handler,
        )

        self.processor.process(
            "prueba argumento"
        )

        handler.assert_called_once_with(
            [
                "prueba",
                "argumento",
            ]
        )

    def test_command_is_registered_in_session(
        self,
    ) -> None:
        self.registry.register(
            "prueba",
            Mock(),
        )

        self.processor.process("prueba")

        (
            self.mz.session.register_command
            .assert_called_once_with("prueba")
        )

    def test_empty_input_does_not_register_command(
        self,
    ) -> None:
        self.mz.input_processor.split.return_value = []

        self.processor.process("")

        (
            self.mz.session.register_command
            .assert_not_called()
        )

    def test_default_commands_are_registered(
        self,
    ) -> None:
        self.assertTrue(
            self.registry.exists("hola")
        )

        self.assertTrue(
            self.registry.exists("preguntar")
        )

        self.assertTrue(
            self.registry.exists(
                "conversacion"
            )
        )


if __name__ == "__main__":
    unittest.main()