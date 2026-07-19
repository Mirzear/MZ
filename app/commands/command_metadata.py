from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandMetadata:
    name: str
    usage: str
    description: str

    def __post_init__(self) -> None:
        normalized_name = self.name.strip().lower()
        normalized_usage = self.usage.strip()
        normalized_description = (
            self.description.strip()
        )

        if not normalized_name:
            raise ValueError(
                "El nombre del comando "
                "no puede estar vacío."
            )

        if not normalized_usage:
            raise ValueError(
                "El uso del comando "
                "no puede estar vacío."
            )

        if not normalized_description:
            raise ValueError(
                "La descripción del comando "
                "no puede estar vacía."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )
        object.__setattr__(
            self,
            "usage",
            normalized_usage,
        )
        object.__setattr__(
            self,
            "description",
            normalized_description,
        )