import unittest

from app.core.system_manager import SystemManager


class TestSystemManager(unittest.TestCase):

    def test_system_manager_can_be_created(self) -> None:
        system = SystemManager()

        self.assertIsInstance(system, SystemManager)


if __name__ == "__main__":
    unittest.main()