from dataclasses import dataclass
from enum import StrEnum

from app.ai.ai_response import AIResponse


class AIStreamEventType(StrEnum):
    TEXT_DELTA = "text_delta"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class AIStreamEvent:
    event_type: AIStreamEventType
    text_delta: str | None = None
    response: AIResponse | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.event_type,
            AIStreamEventType,
        ):
            raise TypeError(
                "event_type debe ser una instancia "
                "de AIStreamEventType."
            )

        normalized_delta = self.text_delta

        if normalized_delta is not None:
            if not isinstance(
                normalized_delta,
                str,
            ):
                raise TypeError(
                    "text_delta debe ser una cadena "
                    "de caracteres o None."
                )

            if not normalized_delta:
                raise ValueError(
                    "text_delta no puede estar vacío."
                )

        if (
            self.response is not None
            and not isinstance(
                self.response,
                AIResponse,
            )
        ):
            raise TypeError(
                "response debe ser una instancia "
                "de AIResponse o None."
            )

        self._validate_payload()

    def _validate_payload(self) -> None:
        if (
            self.event_type
            is AIStreamEventType.TEXT_DELTA
        ):
            if self.text_delta is None:
                raise ValueError(
                    "Un evento de texto debe contener "
                    "un fragmento."
                )

            if self.response is not None:
                raise ValueError(
                    "Un evento de texto no puede "
                    "contener una respuesta final."
                )

            return

        if (
            self.event_type
            is AIStreamEventType.COMPLETED
        ):
            if self.response is None:
                raise ValueError(
                    "Un evento completado debe "
                    "contener una respuesta final."
                )

            if self.text_delta is not None:
                raise ValueError(
                    "Un evento completado no puede "
                    "contener un fragmento de texto."
                )

    @classmethod
    def from_text_delta(
        cls,
        text_delta: str,
    ) -> "AIStreamEvent":
        return cls(
            event_type=(
                AIStreamEventType.TEXT_DELTA
            ),
            text_delta=text_delta,
        )

    @classmethod
    def from_completed_response(
        cls,
        response: AIResponse,
    ) -> "AIStreamEvent":
        return cls(
            event_type=(
                AIStreamEventType.COMPLETED
            ),
            response=response,
        )

    @property
    def is_text_delta(self) -> bool:
        return (
            self.event_type
            is AIStreamEventType.TEXT_DELTA
        )

    @property
    def is_completed(self) -> bool:
        return (
            self.event_type
            is AIStreamEventType.COMPLETED
        )