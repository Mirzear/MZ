import unittest
from datetime import timedelta

from app.core.session_manager import SessionManager


class TestSessionManager(unittest.TestCase):

    def setUp(self) -> None:
        self.session = SessionManager(history_limit=3)

    def test_register_command(self) -> None:
        self.session.register_command("hola")

        self.assertEqual(
            self.session.get_history(),
            ["hola"],
        )

    def test_history_keeps_command_order(self) -> None:
        self.session.register_command("hola")
        self.session.register_command("estado")
        self.session.register_command("salir")

        self.assertEqual(
            self.session.get_history(),
            [
                "hola",
                "estado",
                "salir",
            ],
        )

    def test_history_respects_limit(self) -> None:
        self.session.register_command("uno")
        self.session.register_command("dos")
        self.session.register_command("tres")
        self.session.register_command("cuatro")

        self.assertEqual(
            self.session.get_history(),
            [
                "dos",
                "tres",
                "cuatro",
            ],
        )

    def test_clear_history(self) -> None:
        self.session.register_command("hola")
        self.session.clear_history()

        self.assertEqual(
            self.session.get_history(),
            [],
        )

    def test_get_history_returns_copy(self) -> None:
        self.session.register_command("hola")

        history = self.session.get_history()
        history.append("comando falso")

        self.assertEqual(
            self.session.get_history(),
            ["hola"],
        )

    def test_uptime_is_timedelta(self) -> None:
        uptime = self.session.get_uptime()

        self.assertIsInstance(uptime, timedelta)

    def test_formatted_uptime_has_correct_structure(self) -> None:
        uptime = self.session.get_formatted_uptime()

        parts = uptime.split(":")

        self.assertEqual(len(parts), 3)
        self.assertTrue(all(part.isdigit() for part in parts))


if __name__ == "__main__":
    unittest.main()