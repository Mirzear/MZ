from typing import TYPE_CHECKING

from app.commands.command_decorator import (
    command,
    get_command_name,
)
from app.commands.command_registry import CommandRegistry

if TYPE_CHECKING:
    from app.core.mz import MZ


class CommandProcessor:

    def __init__(
        self,
        mz: "MZ",
        registry: CommandRegistry,
    ) -> None:
        self.mz = mz
        self.registry = registry

        self._register_decorated_commands()

    def _register_decorated_commands(self) -> None:
        """Discover and register decorated command methods."""
        for attribute_name in dir(self):
            attribute = getattr(
                self,
                attribute_name,
            )

            if not callable(attribute):
                continue

            underlying_function = getattr(
                attribute,
                "__func__",
                attribute,
            )

            command_name = get_command_name(
                underlying_function
            )

            if command_name is None:
                continue

            self.registry.register(
                command_name,
                attribute,
            )

    def process(self, user_input: str) -> None:
        parts = self.mz.input_processor.split(
            user_input
        )

        if not parts:
            return

        command_name = (
            self.mz.input_processor.get_command(
                parts
            )
        )

        self.mz.session.register_command(
            command_name
        )

        handler = self.registry.get(
            command_name
        )

        if handler is not None:
            handler(parts)
            return

        suggestion = (
            self.mz.input_processor.suggest_command(
                command_name
            )
        )

        if suggestion:
            print(
                f"{self.mz.name}: "
                f"Comando desconocido: "
                f"'{command_name}'. "
                f"¿Quisiste decir "
                f"'{suggestion}'?"
            )
            return

        print(
            f"{self.mz.name}: "
            f"Comando desconocido: "
            f"'{command_name}'. "
            "Escribí 'ayuda' para ver "
            "los comandos."
        )

    @command("recordar")
    def remember(
        self,
        parts: list[str],
    ) -> None:
        if len(parts) < 3:
            print(
                f"{self.mz.name}: "
                "Uso correcto: "
                "recordar <clave> <valor>"
            )
            return

        key = parts[1].lower()
        value = parts[2]

        self.mz.memory.remember(
            key,
            value,
        )

        print(
            f"{self.mz.name}: "
            f"Recordaré que "
            f"{key} = {value}."
        )

    @command("hola")
    def greet(
        self,
        _parts: list[str],
    ) -> None:
        print(
            f"{self.mz.name}: "
            f"Hola, {self.mz.user}."
        )

    @command("salir")
    def exit_program(
        self,
        _parts: list[str],
    ) -> None:
        print(
            f"{self.mz.name}: "
            f"Hasta luego, "
            f"{self.mz.user}."
        )

        self.mz.running = False

    @command("consultar")
    def recall(
        self,
        parts: list[str],
    ) -> None:
        if len(parts) < 2:
            print(
                f"{self.mz.name}: "
                "Uso correcto: "
                "consultar <clave>"
            )
            return

        key = parts[1].lower()
        value = self.mz.memory.recall(key)

        if value is None:
            print(
                f"{self.mz.name}: "
                "No tengo ningún dato "
                f"guardado como '{key}'."
            )
            return

        print(
            f"{self.mz.name}: "
            f"{key} = {value}"
        )

    @command("olvidar")
    def forget(
        self,
        parts: list[str],
    ) -> None:
        if len(parts) < 2:
            print(
                f"{self.mz.name}: "
                "Uso correcto: "
                "olvidar <clave>"
            )
            return

        key = parts[1].lower()
        forgotten = self.mz.memory.forget(key)

        if forgotten:
            print(
                f"{self.mz.name}: "
                f"Olvidé el dato '{key}'."
            )
            return

        print(
            f"{self.mz.name}: "
            "No tenía ningún dato "
            f"guardado como '{key}'."
        )

    @command("memorias")
    def show_memories(
        self,
        _parts: list[str],
    ) -> None:
        memories = self.mz.memory.get_all()

        if not memories:
            print(
                f"{self.mz.name}: "
                "No tengo recuerdos "
                "guardados."
            )
            return

        print(
            f"{self.mz.name}: "
            "Recuerdos guardados:"
        )

        for key, value in memories.items():
            print(f"- {key}: {value}")

    @command("preguntar")
    def ask_ai(
        self,
        parts: list[str],
    ) -> None:
        if len(parts) < 2:
            print(
                f"{self.mz.name}: "
                "Uso correcto: "
                "preguntar <consulta>"
            )
            return

        prompt = " ".join(parts[1:])
        response = self.mz.ai.ask(prompt)

        self.mz.logger.info(
            "AI response generated"
        )

        print(
            f"{self.mz.name}: "
            f"{response}"
        )

    @command("conversacion")
    def show_conversation(
        self,
        _parts: list[str],
    ) -> None:
        messages = (
            self.mz.ai.get_conversation()
        )

        if not messages:
            print(
                f"{self.mz.name}: "
                "No hay mensajes en "
                "la conversación."
            )
            return

        print(
            f"{self.mz.name}: "
            "Conversación actual:"
        )

        for index, message in enumerate(
            messages,
            start=1,
        ):
            role = message["role"]
            content = message["content"]

            role_name = (
                "Tú"
                if role == "user"
                else self.mz.name
            )

            print(
                f"{index}. "
                f"{role_name}: "
                f"{content}"
            )

    @command("borrar_conversacion")
    def clear_conversation(
        self,
        _parts: list[str],
    ) -> None:
        self.mz.ai.clear_conversation()

        self.mz.logger.info(
            "AI conversation cleared"
        )

        print(
            f"{self.mz.name}: "
            "Conversación eliminada."
        )

    @command("estado")
    def show_status(
        self,
        _parts: list[str],
    ) -> None:
        memories = self.mz.memory.get_all()
        uptime = (
            self.mz.session
            .get_formatted_uptime()
        )
        command_count = len(
            self.mz.session.get_history()
        )

        print(
            f"{self.mz.name}: "
            "Estado del sistema"
        )
        print()
        print(
            f"- Nombre: {self.mz.name}"
        )
        print(
            f"- Versión: {self.mz.version}"
        )
        print(
            f"- Usuario: {self.mz.user}"
        )
        print(
            f"- Tiempo activo: {uptime}"
        )
        print(
            "- Recuerdos guardados: "
            f"{len(memories)}"
        )
        print(
            "- Comandos ejecutados: "
            f"{command_count}"
        )

    @command("historial")
    def show_history(
        self,
        _parts: list[str],
    ) -> None:
        history = (
            self.mz.session.get_history()
        )

        if not history:
            print(
                f"{self.mz.name}: "
                "El historial de esta "
                "sesión está vacío."
            )
            return

        print(
            f"{self.mz.name}: "
            "Historial de la sesión:"
        )

        for position, command_name in enumerate(
            history,
            start=1,
        ):
            print(
                f"{position}. "
                f"{command_name}"
            )

    @command("limpiar")
    def clear_console(
        self,
        _parts: list[str],
    ) -> None:
        self.mz.system.clear_console()

        print(
            f"{self.mz.name}: "
            "Consola limpiada."
        )

    @command("ayuda")
    def show_help(
        self,
        _parts: list[str],
    ) -> None:
        print(
            f"""
{self.mz.name}: Comandos disponibles:

- hola
- recordar <clave> <valor>
- consultar <clave>
- preguntar <consulta>
- conversacion
- borrar_conversacion
- olvidar <clave>
- memorias
- estado
- historial
- limpiar
- ayuda
- salir
"""
        )