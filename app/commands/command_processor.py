from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.mz import MZ


class CommandProcessor:

    def __init__(self, mz: "MZ") -> None:
        self.mz = mz

    def process(self, user_input: str) -> None:
        command = user_input.lower()

        if command in {"salir", "exit", "cerrar"}:
            self.mz.stop()

        elif command in {"hola", "buenas", "hello"}:
            print(f"{self.mz.name}: Hola {self.mz.user}.")

        elif command in {"ayuda", "help"}:
            self.show_help()

        else:
            print(f"{self.mz.name}: Todavía no entiendo ese comando.")

    def show_help(self) -> None:
        print(
            f"""
{self.mz.name}: Comandos disponibles:

- hola
- ayuda
- salir
"""
        )