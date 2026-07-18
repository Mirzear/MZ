from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.mz import MZ


class CommandProcessor:

    def __init__(self, mz: "MZ") -> None:
        self.mz = mz

    def process(self, user_input: str) -> None:
        parts = user_input.strip().split(maxsplit=2)
        command = parts[0].lower()

        self.mz.logger.info(f"Command received: {command}")

        if command in {"salir", "exit", "cerrar"}:
            self.mz.stop()

        elif command in {"hola", "buenas", "hello"}:
            print(f"{self.mz.name}: Hola {self.mz.user}.")

        elif command in {"ayuda", "help"}:
            self.show_help()

        elif command == "recordar":
            self.remember(parts)

        elif command == "consultar":
            self.recall(parts)

        elif command == "olvidar":
            self.forget(parts)

        elif command == "memorias":
            self.show_memories()

        else:
            self.mz.logger.warning(f"Unknown command: {user_input}")
            print(f"{self.mz.name}: Todavía no entiendo ese comando.")

    def remember(self, parts: list[str]) -> None:
        if len(parts) < 3:
            print(
                f"{self.mz.name}: Uso correcto: "
                "recordar <clave> <valor>"
            )
            return

        key = parts[1].lower()
        value = parts[2]

        self.mz.memory.remember(key, value)

        print(f"{self.mz.name}: Recordaré que {key} = {value}.")

    def recall(self, parts: list[str]) -> None:
        if len(parts) < 2:
            print(
                f"{self.mz.name}: Uso correcto: "
                "consultar <clave>"
            )
            return

        key = parts[1].lower()
        value = self.mz.memory.recall(key)

        if value is None:
            print(f"{self.mz.name}: No tengo ningún dato guardado como '{key}'.")
            return

        print(f"{self.mz.name}: {key} = {value}")

    def forget(self, parts: list[str]) -> None:
        if len(parts) < 2:
            print(
                f"{self.mz.name}: Uso correcto: "
                "olvidar <clave>"
            )
            return

        key = parts[1].lower()
        forgotten = self.mz.memory.forget(key)

        if forgotten:
            print(f"{self.mz.name}: Olvidé el dato '{key}'.")
        else:
            print(f"{self.mz.name}: No tenía ningún dato guardado como '{key}'.")

    def show_memories(self) -> None:
        memories = self.mz.memory.get_all()

        if not memories:
            print(f"{self.mz.name}: No tengo recuerdos guardados.")
            return

        print(f"{self.mz.name}: Recuerdos guardados:")

        for key, value in memories.items():
            print(f"- {key}: {value}")

    def show_help(self) -> None:
        print(
            f"""
{self.mz.name}: Comandos disponibles:

- hola
- recordar <clave> <valor>
- consultar <clave>
- olvidar <clave>
- memorias
- ayuda
- salir
"""
        )