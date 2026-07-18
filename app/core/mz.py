from app.core.config_manager import ConfigManager
from app.core.memory_manager import MemoryManager


class MZ:

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.memory = MemoryManager()

        self.name = self.config.get("name", "MZ")
        self.version = self.config.get("version", "0.3.0")
        self.user = self.config.get("user", "Usuario")

        self.running = False

    def start(self) -> None:
        self.running = True

        self.show_startup_message()
        self.run_conversation_loop()

    def show_startup_message(self) -> None:
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
        print("Escribí 'ayuda' para ver los comandos disponibles.")
        print("=" * 50)

    def run_conversation_loop(self) -> None:
        while self.running:
            user_input = input("\nTú: ").strip()

            if not user_input:
                continue

            self.process_input(user_input)

    def process_input(self, user_input: str) -> None:
        command = user_input.lower()

        if command in {"salir", "exit", "cerrar"}:
            self.stop()
        elif command in {"hola", "buenas", "hello"}:
            print(f"{self.name}: Hola {self.user}.")
        elif command in {"ayuda", "help"}:
            self.show_help()
        else:
            print(f"{self.name}: Todavía no entiendo ese comando.")

    def show_help(self) -> None:
        print(f"""
{self.name}: Comandos disponibles:

- hola
- ayuda
- salir
""")

    def stop(self) -> None:
        print(f"{self.name}: Hasta luego, {self.user}.")
        self.running = False