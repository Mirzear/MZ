from app.commands.command_registry import CommandRegistry
from typing import TYPE_CHECKING
from app.commands.command_registry import (
    CommandRegistry,
)

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

        self._register_commands()

    def _register_commands(self) -> None:
        self.registry.register(
            "hola",
            self.greet,
        )
        self.registry.register(
            "ayuda",
            self.show_help,
        )
        self.registry.register(
            "salir",
            self.exit_program,
        )
        self.registry.register(
            "recordar",
            self.remember,
        )
        self.registry.register(
            "consultar",
            self.recall,
        )
        self.registry.register(
            "olvidar",
            self.forget,
        )
        self.registry.register(
            "memorias",
            self.show_memories,
        )
        self.registry.register(
            "preguntar",
            self.ask_ai,
        )
        self.registry.register(
            "estado",
            self.show_status,
        )
        self.registry.register(
            "historial",
            self.show_history,
        )
        self.registry.register(
            "limpiar",
            self.clear_console,
        )
        self.registry.register(
            "conversacion",
            self.show_conversation,
        )
        self.registry.register(
            "borrar_conversacion",
            self.clear_conversation,
        )

    def process(self, user_input: str) -> None:
        parts = self.mz.input_processor.split(user_input)

        if not parts:
            return

        command = self.mz.input_processor.get_command(
            parts
        )

        self.mz.session.register_command(command)

        handler = self.registry.get(command)

        if handler is not None:
            handler(parts)
            return

        suggestion = (
            self.mz.input_processor.suggest_command(
                command
            )
        )

        if suggestion:
            print(
                f"{self.mz.name}: "
                f"Comando desconocido: '{command}'. "
                f"¿Quisiste decir '{suggestion}'?"
            )
            return

        print(
            f"{self.mz.name}: "
            f"Comando desconocido: '{command}'. "
            "Escribí 'ayuda' para ver los comandos."
        )

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
    
    def greet(self, _parts: list[str]) -> None:
        print(f"{self.mz.name}: Hola, {self.mz.user}.")


    def exit_program(self, _parts: list[str]) -> None:
        print(f"{self.mz.name}: Hasta luego, {self.mz.user}.")
        self.mz.running = False

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

    def show_memories(self, _parts: list[str]) -> None:
        memories = self.mz.memory.get_all()

        if not memories:
            print(f"{self.mz.name}: No tengo recuerdos guardados.")
            return

        print(f"{self.mz.name}: Recuerdos guardados:")

        for key, value in memories.items():
            print(f"- {key}: {value}")

    def ask_ai(self, parts: list[str]) -> None:
        if len(parts) < 2:
            print(
                  f"{self.mz.name}: Uso correcto: "
                 "preguntar <consulta>"
             )
            return

        prompt = " ".join(parts[1:])
        response = self.mz.ai.ask(prompt)

        self.mz.logger.info("AI response generated")

        print(f"{self.mz.name}: {response}")

    def show_conversation(self, _parts: list[str]) -> None:
        messages = self.mz.ai.get_conversation()

        if not messages:
            print(
                f"{self.mz.name}: "
                "No hay mensajes en la conversación."
            )
            return

        print(f"{self.mz.name}: Conversación actual:")

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
                f"{index}. {role_name}: {content}"
            )

    def clear_conversation(self, _parts: list[str]) -> None:
        self.mz.ai.clear_conversation()

        self.mz.logger.info(
            "AI conversation cleared"
        )

        print(
            f"{self.mz.name}: "
            "Conversación eliminada."
        )

    def show_status(self, _parts: list[str]) -> None:
        memories = self.mz.memory.get_all()
        uptime = self.mz.session.get_formatted_uptime()

        print(f"""
        {self.mz.name}: Estado del sistema

        - Nombre: {self.mz.name}
        - Versión: {self.mz.version}
        - Usuario: {self.mz.user}
        - Tiempo activo: {uptime}
        - Recuerdos guardados: {len(memories)}
        - Comandos ejecutados: {len(self.mz.session.get_history())}
        """)


    def show_history(self, _parts: list[str]) -> None:
        history = self.mz.session.get_history()

        if not history:
            print(f"{self.mz.name}: El historial de esta sesión está vacío.")
            return

        print(f"{self.mz.name}: Historial de la sesión:")

        for position, command in enumerate(
            history, 
            start=1
        ):
            print(f"{position}. {command}")


    def clear_console(self, _parts: list[str]) -> None:
        self.mz.system.clear_console()

        print(f"{self.mz.name}: Consola limpiada.")

    def show_help(self, _parts: list[str]) -> None:
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