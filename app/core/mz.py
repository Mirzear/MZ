from app.core.config_manager import ConfigManager 
class MZ:

    def __init__(self):
        self.config = ConfigManager()

        self.name = self.config.get("name")
        self.version = self.config.get("version")
        self.user = self.config.get("user")


    def start(self):

        print("=" * 50)
        print(f"{self.name} v{self.version}")
        print("=" * 50)

        print("Inicializando sistema...")
        print("[✔] Núcleo cargado")
        print("[✔] Configuración cargada")

        print("")
        print(f"Hola {self.user}.")
        print(f"{self.name} está operativo.")

        print("=" * 50)