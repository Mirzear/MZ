import json
from pathlib import Path
from typing import Any

class ConfigManager:

    def __init__(self):
        self.base_path = Path(__file__).resolve().parent.parent.parent
        self.ruta = self.base_path / "config" / "config.json"

        self.datos = self.load()


    def load(self):
        if self.ruta.exists():
            with open(self.ruta, "r", encoding="utf-8") as file:
                return json.load(file)

        return {}


    def get(self, key: str, default: Any = None) -> Any:
        return self.datos.get(key)