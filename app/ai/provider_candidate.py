from dataclasses import dataclass

from app.ai.ai_provider import AIProvider


@dataclass(frozen=True, slots=True)
class ProviderCandidate:
    name: str
    provider: AIProvider
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "name debe ser una cadena "
                "de caracteres."
            )

        normalized_name = (
            self.name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "El nombre del proveedor no "
                "puede estar vacío."
            )

        if not isinstance(
            self.provider,
            AIProvider,
        ):
            raise TypeError(
                "provider debe cumplir el "
                "contrato AIProvider."
            )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise TypeError(
                "enabled debe ser un valor "
                "booleano."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )