import json
from pathlib import Path
from typing import Any


class ConfigManager:

    def __init__(
        self,
        config_path: Path | None = None,
    ) -> None:
        self.base_path = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        self.ruta = (
            config_path
            if config_path is not None
            else (
                self.base_path
                / "config"
                / "config.json"
            )
        )

        self.datos = self.load()

    def load(self) -> dict[str, Any]:
        if not self.ruta.exists():
            return {}

        with self.ruta.open(
            "r",
            encoding="utf-8",
        ) as file:
            loaded_data = json.load(file)

        if not isinstance(
            loaded_data,
            dict,
        ):
            raise ValueError(
                "El archivo de configuración "
                "debe contener un objeto JSON."
            )

        return loaded_data

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.datos.get(
            key,
            default,
        )

    def get_section(
        self,
        section: str,
    ) -> dict[str, Any]:
        value = self.get(
            section,
            {},
        )

        if not isinstance(
            value,
            dict,
        ):
            return {}

        return value