import json
import tempfile
import unittest
from pathlib import Path

from app.core.config_manager import (
    ConfigManager,
)


class TestConfigManager(
    unittest.TestCase
):

    def _create_config_file(
        self,
        data: object,
    ) -> tuple[
        tempfile.TemporaryDirectory,
        Path,
    ]:
        temporary_directory = (
            tempfile.TemporaryDirectory()
        )

        config_path = (
            Path(temporary_directory.name)
            / "config.json"
        )

        with config_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
            )

        return (
            temporary_directory,
            config_path,
        )

    def test_loads_configuration(
        self,
    ) -> None:
        temporary_directory, path = (
            self._create_config_file(
                {
                    "name": "MZ",
                    "version": "2.2.0",
                }
            )
        )

        self.addCleanup(
            temporary_directory.cleanup
        )

        manager = ConfigManager(
            config_path=path
        )

        self.assertEqual(
            manager.get("name"),
            "MZ",
        )
        self.assertEqual(
            manager.get("version"),
            "2.2.0",
        )

    def test_returns_default_value(
        self,
    ) -> None:
        temporary_directory, path = (
            self._create_config_file({})
        )

        self.addCleanup(
            temporary_directory.cleanup
        )

        manager = ConfigManager(
            config_path=path
        )

        self.assertEqual(
            manager.get(
                "missing",
                "default",
            ),
            "default",
        )

    def test_missing_file_returns_empty_data(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_path = (
                Path(directory)
                / "missing.json"
            )

            manager = ConfigManager(
                config_path=missing_path
            )

            self.assertEqual(
                manager.datos,
                {},
            )

    def test_returns_configuration_section(
        self,
    ) -> None:
        temporary_directory, path = (
            self._create_config_file(
                {
                    "ai": {
                        "enabled": True,
                    }
                }
            )
        )

        self.addCleanup(
            temporary_directory.cleanup
        )

        manager = ConfigManager(
            config_path=path
        )

        self.assertEqual(
            manager.get_section("ai"),
            {
                "enabled": True,
            },
        )

    def test_invalid_section_returns_empty_dict(
        self,
    ) -> None:
        temporary_directory, path = (
            self._create_config_file(
                {
                    "ai": "invalid",
                }
            )
        )

        self.addCleanup(
            temporary_directory.cleanup
        )

        manager = ConfigManager(
            config_path=path
        )

        self.assertEqual(
            manager.get_section("ai"),
            {},
        )

    def test_rejects_non_object_json(
        self,
    ) -> None:
        temporary_directory, path = (
            self._create_config_file(
                ["invalid"]
            )
        )

        self.addCleanup(
            temporary_directory.cleanup
        )

        with self.assertRaises(
            ValueError
        ):
            ConfigManager(
                config_path=path
            )


if __name__ == "__main__":
    unittest.main()