from difflib import get_close_matches


class InputProcessor:

    def __init__(self) -> None:
        self.command_aliases = {
            "recordá": "recordar",
            "recuerda": "recordar",
            "guardar": "recordar",
            "acordate": "recordar",

            "consulta": "consultar",
            "buscar": "consultar",
            "ver": "consultar",

            "borrar": "olvidar",
            "eliminar": "olvidar",

            "recuerdos": "memorias",

            "adios": "salir",
            "adiós": "salir",
            "chau": "salir",

            "help": "ayuda",
            "hello": "hola",
            "exit": "salir",

            "ask": "preguntar",
            "consultaia": "preguntar",

            "chat": "conversacion",
            "borrarchat": "borrar_conversacion",
        }

        self.valid_commands = {
            "hola",
            "ayuda",
            "salir",
            "recordar",
            "consultar",
            "olvidar",
            "memorias",
            "preguntar",
            "conversacion",
            "borrar_conversacion",
        }

    def normalize(self, user_input: str) -> str:
        """Normalize raw user input."""
        return " ".join(user_input.strip().split())

    def split(self, user_input: str) -> list[str]:
        """Split normalized input into command, key and value."""
        normalized_input = self.normalize(user_input)

        if not normalized_input:
            return []

        return normalized_input.split(maxsplit=2)

    def get_command(self, parts: list[str]) -> str:
        """Return the normalized command."""
        if not parts:
            return ""

        raw_command = parts[0].lower()

        return self.command_aliases.get(raw_command, raw_command)

    def suggest_command(self, command: str) -> str | None:
        """Suggest the closest valid command."""
        matches = get_close_matches(
            command,
            self.valid_commands,
            n=1,
            cutoff=0.7,
        )

        if not matches:
            return None

        return matches[0]