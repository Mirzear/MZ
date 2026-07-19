from app.ai.ai_service import AIService
from app.ai.mock_ai_provider import MockAIProvider
from app.commands.command_processor import CommandProcessor
from app.commands.command_registry import CommandRegistry
from app.core.config_manager import ConfigManager
from app.core.input_processor import InputProcessor
from app.core.logger import Logger
from app.core.memory_manager import MemoryManager
from app.core.session_manager import SessionManager
from app.core.system_manager import SystemManager
from app.tools.core_tools import CoreTools
from app.tools.tool_loader import ToolLoader
from app.tools.tool_registry import ToolRegistry


class MZ:

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.session = SessionManager()
        self.logger = Logger()
        self.memory = MemoryManager()
        self.system = SystemManager()

        self.ai = AIService(
            provider=MockAIProvider()
        )

        self.tool_registry = ToolRegistry()

        self.tool_loader = ToolLoader(
            registry=self.tool_registry,
        )

        self.core_tools = CoreTools()

        self.tool_loader.load(
            self.core_tools
        )

        self.command_registry = CommandRegistry()

        self.input_processor = InputProcessor(
            registry=self.command_registry,
        )

        self.command_processor = CommandProcessor(
            mz=self,
            registry=self.command_registry,
        )

        self.name = self.config.get(
            "name",
            "MZ",
        )
        self.version = self.config.get(
            "version",
            "0.3.0",
        )
        self.user = self.config.get(
            "user",
            "Usuario",
        )

        self.running = False

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
        print("[✔] Servicio de IA cargado")
        print(
            "[✔] Herramientas cargadas: "
            f"{self.tool_registry.count()}"
        )

        print()
        print(f"Hola {self.user}.")
        print(f"{self.name} está operativo.")
        print(
            "Escribí 'ayuda' para ver los "
            "comandos disponibles."
        )
        print("=" * 50)

    def run_conversation_loop(self) -> None:
        while self.running:
            user_input = input("\nTú: ").strip()

            if not user_input:
                continue

            self.command_processor.process(
                user_input
            )

    def stop(self) -> None:
        print(
            f"{self.name}: "
            f"Hasta luego, {self.user}."
        )
        self.logger.info("MZ stopped")
        self.running = False