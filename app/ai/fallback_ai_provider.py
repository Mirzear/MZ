from collections.abc import (
    Callable,
    Sequence,
)
from time import monotonic

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)
from app.ai.ai_response import AIResponse
from app.ai.provider_candidate import (
    ProviderCandidate,
)


class FallbackAIProvider:

    def __init__(
        self,
        providers: Sequence[
            ProviderCandidate
        ],
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if not isinstance(
            providers,
            Sequence,
        ):
            raise TypeError(
                "providers debe ser una "
                "secuencia."
            )

        normalized_providers = list(
            providers
        )

        if not normalized_providers:
            raise ValueError(
                "Debe configurarse al menos un "
                "proveedor."
            )

        for candidate in normalized_providers:
            if not isinstance(
                candidate,
                ProviderCandidate,
            ):
                raise TypeError(
                    "Todos los elementos deben "
                    "ser ProviderCandidate."
                )

        provider_names = [
            candidate.name
            for candidate
            in normalized_providers
        ]

        if (
            len(provider_names)
            != len(set(provider_names))
        ):
            raise ValueError(
                "No puede haber proveedores con "
                "nombres duplicados."
            )

        if not callable(clock):
            raise TypeError(
                "clock debe ser invocable."
            )

        self._providers = tuple(
            normalized_providers
        )
        self._clock = clock
        self._unavailable_until: dict[
            str,
            float,
        ] = {}

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        attempted_providers: list[str] = []

        for candidate in self._providers:
            if not candidate.enabled:
                continue

            if self._is_in_cooldown(
                candidate.name
            ):
                continue

            attempted_providers.append(
                candidate.name
            )

            try:
                return (
                    candidate.provider
                    .generate_response(
                        prompt=prompt,
                        context=context,
                    )
                )
            except AIProviderError as error:
                if not error.fallback_allowed:
                    raise

                self._apply_cooldown(
                    provider_name=(
                        candidate.name
                    ),
                    cooldown_seconds=(
                        error.cooldown_seconds
                    ),
                )

        if attempted_providers:
            attempted_text = ", ".join(
                attempted_providers
            )

            message = (
                "Todos los proveedores "
                "disponibles fallaron: "
                f"{attempted_text}."
            )
        else:
            message = (
                "No hay proveedores disponibles "
                "en este momento."
            )

        raise AIProviderError(
            message,
            kind=(
                AIProviderErrorKind
                .SERVICE_UNAVAILABLE
            ),
            provider_name="fallback",
            cooldown_seconds=0,
        )

    def get_available_provider_names(
        self,
    ) -> list[str]:
        return [
            candidate.name
            for candidate in self._providers
            if (
                candidate.enabled
                and not self._is_in_cooldown(
                    candidate.name
                )
            )
        ]

    def get_cooldown_remaining(
        self,
        provider_name: str,
    ) -> float:
        normalized_name = (
            self._normalize_provider_name(
                provider_name
            )
        )

        unavailable_until = (
            self._unavailable_until.get(
                normalized_name
            )
        )

        if unavailable_until is None:
            return 0.0

        remaining = (
            unavailable_until
            - self._clock()
        )

        return max(
            0.0,
            remaining,
        )

    def clear_cooldowns(self) -> None:
        self._unavailable_until.clear()

    def _is_in_cooldown(
        self,
        provider_name: str,
    ) -> bool:
        remaining = (
            self.get_cooldown_remaining(
                provider_name
            )
        )

        if remaining > 0:
            return True

        self._unavailable_until.pop(
            provider_name,
            None,
        )

        return False

    def _apply_cooldown(
        self,
        provider_name: str,
        cooldown_seconds: float,
    ) -> None:
        if cooldown_seconds <= 0:
            return

        self._unavailable_until[
            provider_name
        ] = (
            self._clock()
            + cooldown_seconds
        )

    @staticmethod
    def _normalize_provider_name(
        provider_name: str,
    ) -> str:
        if not isinstance(
            provider_name,
            str,
        ):
            raise TypeError(
                "provider_name debe ser una "
                "cadena de caracteres."
            )

        normalized_name = (
            provider_name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "provider_name no puede estar "
                "vacío."
            )

        return normalized_name