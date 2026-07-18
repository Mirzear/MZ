import os
from typing import TYPE_CHECKING
from urllib import response

if TYPE_CHECKING:
    from app.core.mz import MZ


class CommandProcessor:

    def __init__(self, mz: "MZ") -> None:
        self.mz = mz

    def process(self, user_input: str) -> None:
        parts = self.mz.input_processor.split(user_input)
        command = self.mz.input_processor.get_command(parts)
        
        if not command:
            return

        self.mz.logger.info(f"Command received: {command}")
        self.mz.session.register_command(command)

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
        
        elif command in {"estado", "status"}:
            self.show_status()

        elif command in {"historial", "history"}:
            self.show_history()

        elif command in {"limpiar", "clear"}:
            self.clear_console()

        elif command in {"preguntar", "ask"}:
            self.ask_ai(parts)
        
        elif command == "conversacion":
            self.show_conversation()

        elif command == "borrar_conversacion":
            self.clear_conversation()

        else:
            suggestion = self.mz.input_processor.suggest_command(command)

            self.mz.logger.warning(f"Unknown command: {user_input}")

            if suggestion:
                print(
                    f"{self.mz.name}: Comando desconocido: '{command}'. "
                    f"Quizás quisiste decir '{suggestion}'."
                )
                
            else:
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

    def show_conversation(self) -> None:
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

    def clear_conversation(self) -> None:
        self.mz.ai.clear_conversation()

        self.mz.logger.info(
            "AI conversation cleared"
        )

        print(
            f"{self.mz.name}: "
            "Conversación eliminada."
        )

    def show_status(self) -> None:
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


    def show_history(self) -> None:
        history = self.mz.session.get_history()

        if not history:
            print(f"{self.mz.name}: El historial de esta sesión está vacío.")
            return

        print(f"{self.mz.name}: Historial de la sesión:")

        for position, command in enumerate(history, start=1):
          print(f"{position}. {command}")


    def clear_console(self) -> None:
        self.mz.system.clear_console()

        print(f"{self.mz.name}: Consola limpiada.")

    def show_help(self) -> None:
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