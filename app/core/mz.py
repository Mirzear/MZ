from app.core.config_manager import ConfigManager
from app.core.memory_manager import MemoryManager


class MZ:

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.memory = MemoryManager()

        self.name = self.config.get("name")
        self.version = self.config.get("version")
        self.user = self.config.get("user")

    def start(self) -> None:
        print("=" * 50)
        print(f"{self.name} v{self.version}")
        print("=" * 50)

        print("Inicializando sistema...")
        print("[✔] Núcleo cargado")
        print("[✔] Configuración cargada")
        print("[✔] Memoria cargada")

        print()
        print(f"Hola {self.user}.")
        print(f"{self.name} está operativo.")

        print("=" * 50)

        self.memory.remember("creator", "Agustin Pereira")

        creator = self.memory.recall("creator")

        print(f"Memoria cargada: creador = {creator}")