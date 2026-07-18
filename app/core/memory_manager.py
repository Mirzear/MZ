import json
from pathlib import Path
from typing import Any


class MemoryManager:
    def __init__(self, path: Path | None = None) -> None:
        self.base_path = Path(__file__).resolve().parents[2]
        
        self.path = path or (
            self.base_path / "data" / "memory.json"
        )

        self.data: dict[str, Any] = {}

        self.load()

    def load(self) -> None:
        """Load persistent memory from the JSON file."""
        try:
            with self.path.open("r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
            self.save()
        except json.JSONDecodeError:
            print("Advertencia: el archivo de memoria está dañado.")
            self.data = {}

    def save(self) -> None:
        """Save persistent memory to the JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def remember(self, key: str, value: Any) -> None:
        """Store a value in persistent memory."""
        self.data[key] = value
        self.save()

    def recall(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from persistent memory."""
        return self.data.get(key, default)

    def forget(self, key: str) -> bool:
        """Remove a value from persistent memory."""
        if key not in self.data:
            return False

        del self.data[key]
        self.save()
        return True

    def get_all(self) -> dict[str, Any]:
        """Return a copy of all stored memories."""
        return self.data.copy()