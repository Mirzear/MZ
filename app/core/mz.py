from app.commands.command_processor import CommandProcessor
from app.core.config_manager import ConfigManager
from app.core.memory_manager import MemoryManager
from app.core.logger import Logger
from app.core.input_processor import InputProcessor
from app.core.session_manager import SessionManager
from app.core.system_manager import SystemManager

class MZ:

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.session = SessionManager()
        self.input_processor = InputProcessor()
        self.logger = Logger()
        self.memory = MemoryManager()
        self.system = SystemManager()

        self.name = self.config.get("name", "MZ")
        self.version = self.config.get("version", "0.3.0")
        self.user = self.config.get("user", "Usuario")

        self.running = False
        self.command_processor = CommandProcessor(self)

    def start(self) -> None:
        self.running = True

        self.logger.info("MZ started")

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
        print("[✔] Procesador de comandos cargado")
        print("[✔] Procesador de entrada cargado")
        print("[✔] Gestor de sesión cargado")
        print("[✔] Gestor del sistema cargado")

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

            self.command_processor.process(user_input)

    def stop(self) -> None:
        print(f"{self.name}: Hasta luego, {self.user}.")
        self.logger.info("MZ stopped")
        self.running = False