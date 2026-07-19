from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class ConversationRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

    @classmethod
    def from_value(
        cls,
        value: "ConversationRole | str",
    ) -> "ConversationRole":
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise TypeError(
                "role debe ser una cadena de caracteres "
                "o una instancia de ConversationRole."
            )

        normalized_value = value.strip().lower()

        try:
            return cls(normalized_value)
        except ValueError as error:
            raise ValueError(
                f"Rol de conversación inválido: '{value}'."
            ) from error


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    role: ConversationRole
    content: str

    def __post_init__(self) -> None:
        normalized_role = ConversationRole.from_value(
            self.role
        )

        if not isinstance(self.content, str):
            raise TypeError(
                "content debe ser una cadena de caracteres."
            )

        cleaned_content = self.content.strip()

        if not cleaned_content:
            raise ValueError(
                "El contenido del mensaje no puede estar vacío."
            )

        object.__setattr__(
            self,
            "role",
            normalized_role,
        )
        object.__setattr__(
            self,
            "content",
            cleaned_content,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "ConversationMessage":
        if not isinstance(data, Mapping):
            raise TypeError(
                "data debe ser un mapeo."
            )

        if "role" not in data:
            raise ValueError(
                "El mensaje no contiene el campo 'role'."
            )

        if "content" not in data:
            raise ValueError(
                "El mensaje no contiene el campo 'content'."
            )

        return cls(
            role=ConversationRole.from_value(
                data["role"]
            ),
            content=data["content"],
        )