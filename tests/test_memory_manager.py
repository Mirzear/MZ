import tempfile
import unittest
from pathlib import Path

from app.core.memory_manager import MemoryManager


class TestMemoryManager(unittest.TestCase):

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()

        self.memory_path = (
            Path(self.temporary_directory.name)
            / "memory.json"
        )

        self.memory = MemoryManager(self.memory_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_remember_and_recall_value(self) -> None:
        self.memory.remember("city", "Buenos Aires")

        result = self.memory.recall("city")

        self.assertEqual(result, "Buenos Aires")

    def test_memory_is_persistent(self) -> None:
        self.memory.remember("color", "azul")

        new_memory = MemoryManager(self.memory_path)

        result = new_memory.recall("color")

        self.assertEqual(result, "azul")

    def test_recall_unknown_key_returns_default(self) -> None:
        result = self.memory.recall(
            "unknown",
            "not found",
        )

        self.assertEqual(result, "not found")

    def test_forget_existing_value(self) -> None:
        self.memory.remember("food", "milanesa")

        forgotten = self.memory.forget("food")

        self.assertTrue(forgotten)
        self.assertIsNone(self.memory.recall("food"))

    def test_forget_unknown_value_returns_false(self) -> None:
        forgotten = self.memory.forget("unknown")

        self.assertFalse(forgotten)

    def test_get_all_returns_stored_memories(self) -> None:
        self.memory.remember("city", "Buenos Aires")
        self.memory.remember("color", "azul")

        memories = self.memory.get_all()

        self.assertEqual(
            memories,
            {
                "city": "Buenos Aires",
                "color": "azul",
            },
        )


if __name__ == "__main__":
    unittest.main()