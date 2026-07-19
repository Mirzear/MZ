from dataclasses import dataclass
from enum import StrEnum

from app.tools.tool_call import ToolCall


class AIResponseType(StrEnum):
    TEXT = "text"
    TOOL_CALL = "tool_call"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class AIResponse:
    response_type: AIResponseType
    content: str | None = None
    tool_call: ToolCall | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.response_type,
            AIResponseType,
        ):
            raise TypeError(
                "response_type debe ser una "
                "instancia de AIResponseType."
            )

        normalized_content = self.content
        normalized_error = self.error_message

        if normalized_content is not None:
            if not isinstance(
                normalized_content,
                str,
            ):
                raise TypeError(
                    "content debe ser una cadena "
                    "de caracteres o None."
                )

            normalized_content = (
                normalized_content.strip()
            )

        if normalized_error is not None:
            if not isinstance(
                normalized_error,
                str,
            ):
                raise TypeError(
                    "error_message debe ser una "
                    "cadena de caracteres o None."
                )

            normalized_error = (
                normalized_error.strip()
            )

        if (
            self.tool_call is not None
            and not isinstance(
                self.tool_call,
                ToolCall,
            )
        ):
            raise TypeError(
                "tool_call debe ser una instancia "
                "de ToolCall o None."
            )

        self._validate_payload(
            content=normalized_content,
            error_message=normalized_error,
        )

        object.__setattr__(
            self,
            "content",
            normalized_content,
        )
        object.__setattr__(
            self,
            "error_message",
            normalized_error,
        )

    def _validate_payload(
        self,
        content: str | None,
        error_message: str | None,
    ) -> None:
        if (
            self.response_type
            is AIResponseType.TEXT
        ):
            if not content:
                raise ValueError(
                    "Una respuesta de texto debe "
                    "contener contenido."
                )

            if self.tool_call is not None:
                raise ValueError(
                    "Una respuesta de texto no puede "
                    "contener un ToolCall."
                )

            if error_message is not None:
                raise ValueError(
                    "Una respuesta de texto no puede "
                    "contener un mensaje de error."
                )

            return

        if (
            self.response_type
            is AIResponseType.TOOL_CALL
        ):
            if self.tool_call is None:
                raise ValueError(
                    "Una respuesta de herramienta "
                    "debe contener un ToolCall."
                )

            if content is not None:
                raise ValueError(
                    "Una respuesta de herramienta "
                    "no puede contener texto."
                )

            if error_message is not None:
                raise ValueError(
                    "Una respuesta de herramienta "
                    "no puede contener un mensaje "
                    "de error."
                )

            return

        if (
            self.response_type
            is AIResponseType.ERROR
        ):
            if not error_message:
                raise ValueError(
                    "Una respuesta de error debe "
                    "contener un mensaje."
                )

            if content is not None:
                raise ValueError(
                    "Una respuesta de error no puede "
                    "contener texto."
                )

            if self.tool_call is not None:
                raise ValueError(
                    "Una respuesta de error no puede "
                    "contener un ToolCall."
                )

    @classmethod
    def from_text(
        cls,
        content: str,
    ) -> "AIResponse":
        return cls(
            response_type=AIResponseType.TEXT,
            content=content,
        )

    @classmethod
    def from_tool_call(
        cls,
        tool_call: ToolCall,
    ) -> "AIResponse":
        return cls(
            response_type=(
                AIResponseType.TOOL_CALL
            ),
            tool_call=tool_call,
        )

    @classmethod
    def from_error(
        cls,
        error_message: str,
    ) -> "AIResponse":
        return cls(
            response_type=AIResponseType.ERROR,
            error_message=error_message,
        )

    @property
    def is_text(self) -> bool:
        return (
            self.response_type
            is AIResponseType.TEXT
        )

    @property
    def is_tool_call(self) -> bool:
        return (
            self.response_type
            is AIResponseType.TOOL_CALL
        )

    @property
    def is_error(self) -> bool:
        return (
            self.response_type
            is AIResponseType.ERROR
        )

    @property
    def succeeded(self) -> bool:
        return not self.is_error

    def to_user_text(self) -> str:
        if self.is_text:
            return self.content or ""

        if self.is_tool_call:
            tool_name = (
                self.tool_call.tool_name
                if self.tool_call is not None
                else "desconocida"
            )

            return (
                "La IA solicitó ejecutar la "
                f"herramienta '{tool_name}'."
            )

        return (
            self.error_message
            or "Se produjo un error desconocido."
        )