from enum import StrEnum


class AIProviderErrorKind(StrEnum):
    RATE_LIMIT = "rate_limit"
    QUOTA_EXHAUSTED = "quota_exhausted"
    TIMEOUT = "timeout"
    SERVICE_UNAVAILABLE = (
        "service_unavailable"
    )
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    INVALID_REQUEST = "invalid_request"
    INVALID_RESPONSE = "invalid_response"
    UNKNOWN = "unknown"


class AIProviderError(Exception):

    _FALLBACK_ALLOWED_KINDS = {
        AIProviderErrorKind.RATE_LIMIT,
        AIProviderErrorKind.QUOTA_EXHAUSTED,
        AIProviderErrorKind.TIMEOUT,
        AIProviderErrorKind.SERVICE_UNAVAILABLE,
        AIProviderErrorKind.NETWORK,
    }

    _DEFAULT_COOLDOWNS = {
        AIProviderErrorKind.RATE_LIMIT: 60.0,
        AIProviderErrorKind.QUOTA_EXHAUSTED: (
            3600.0
        ),
        AIProviderErrorKind.TIMEOUT: 30.0,
        AIProviderErrorKind.SERVICE_UNAVAILABLE: (
            60.0
        ),
        AIProviderErrorKind.NETWORK: 30.0,
    }

    def __init__(
        self,
        message: str,
        *,
        kind: AIProviderErrorKind,
        provider_name: str | None = None,
        cooldown_seconds: float | None = None,
    ) -> None:
        if not isinstance(message, str):
            raise TypeError(
                "message debe ser una cadena "
                "de caracteres."
            )

        normalized_message = message.strip()

        if not normalized_message:
            raise ValueError(
                "El mensaje del error no puede "
                "estar vacío."
            )

        if not isinstance(
            kind,
            AIProviderErrorKind,
        ):
            raise TypeError(
                "kind debe ser una instancia de "
                "AIProviderErrorKind."
            )

        normalized_provider_name = (
            self._normalize_provider_name(
                provider_name
            )
        )

        if cooldown_seconds is not None:
            if not isinstance(
                cooldown_seconds,
                int | float,
            ):
                raise TypeError(
                    "cooldown_seconds debe ser "
                    "numérico o None."
                )

            if isinstance(
                cooldown_seconds,
                bool,
            ):
                raise TypeError(
                    "cooldown_seconds debe ser "
                    "numérico o None."
                )

            if cooldown_seconds < 0:
                raise ValueError(
                    "cooldown_seconds no puede "
                    "ser negativo."
                )

            normalized_cooldown = float(
                cooldown_seconds
            )
        else:
            normalized_cooldown = (
                self._DEFAULT_COOLDOWNS.get(
                    kind,
                    0.0,
                )
            )

        self.message = normalized_message
        self.kind = kind
        self.provider_name = (
            normalized_provider_name
        )
        self.cooldown_seconds = (
            normalized_cooldown
        )

        super().__init__(
            self._build_exception_message()
        )

    @property
    def fallback_allowed(self) -> bool:
        return (
            self.kind
            in self._FALLBACK_ALLOWED_KINDS
        )

    def _build_exception_message(
        self,
    ) -> str:
        if self.provider_name is None:
            return self.message

        return (
            f"[{self.provider_name}] "
            f"{self.message}"
        )

    @staticmethod
    def _normalize_provider_name(
        provider_name: str | None,
    ) -> str | None:
        if provider_name is None:
            return None

        if not isinstance(
            provider_name,
            str,
        ):
            raise TypeError(
                "provider_name debe ser una "
                "cadena de caracteres o None."
            )

        normalized_name = (
            provider_name.strip().lower()
        )

        if not normalized_name:
            raise ValueError(
                "provider_name no puede ser una "
                "cadena vacía."
            )

        return normalized_name