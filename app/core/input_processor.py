from difflib import get_close_matches

from app.commands.command_registry import CommandRegistry


class InputProcessor:

    def __init__(
        self,
        registry: CommandRegistry,
    ) -> None:
        self.registry = registry

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

    def normalize(self, user_input: str) -> str:
        """Normalize raw user input."""
        return " ".join(
            user_input.strip().split()
        )

    def split(
        self,
        user_input: str,
    ) -> list[str]:
        """Split normalized input into command, key and value."""
        normalized_input = self.normalize(
            user_input
        )

        if not normalized_input:
            return []

        return normalized_input.split(
            maxsplit=2
        )

    def get_command(
        self,
        parts: list[str],
    ) -> str:
        """Return the normalized command."""
        if not parts:
            return ""

        raw_command = parts[0].lower()

        return self.command_aliases.get(
            raw_command,
            raw_command,
        )

    def suggest_command(
        self,
        command: str,
    ) -> str | None:
        """Suggest the closest registered command."""
        possible_commands = (
            self.registry.get_commands()
            | set(self.command_aliases)
        )

        matches = get_close_matches(
            command,
            possible_commands,
            n=1,
            cutoff=0.7,
        )

        if not matches:
            return None

        suggestion = matches[0]

        return self.command_aliases.get(
            suggestion,
            suggestion,
        )