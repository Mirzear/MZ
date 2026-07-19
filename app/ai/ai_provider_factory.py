import os
from collections.abc import Mapping
from typing import Any

from dotenv import load_dotenv

from app.ai.ai_provider import AIProvider
from app.ai.fallback_ai_provider import (
    FallbackAIProvider,
)
from app.ai.gemini_ai_provider import (
    GeminiAIProvider,
)
from app.ai.mock_ai_provider import (
    MockAIProvider,
)
from app.ai.provider_candidate import (
    ProviderCandidate,
)
from app.core.config_manager import ConfigManager


class AIProviderFactory:

    def __init__(
        self,
        config: ConfigManager,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        if not isinstance(
            config,
            ConfigManager,
        ):
            raise TypeError(
                "config debe ser una instancia "
                "de ConfigManager."
            )

        self._config = config

        if environ is None:
            load_dotenv(
                dotenv_path=(
                    self._config.base_path
                    / ".env"
                ),
                override=False,
            )

            self._environ: Mapping[
                str,
                str,
            ] = os.environ
        else:
            self._environ = environ

    def create(self) -> AIProvider:
        candidates = (
            self._create_candidates()
        )

        if not candidates:
            return MockAIProvider()

        if len(candidates) == 1:
            return candidates[0].provider

        return FallbackAIProvider(
            providers=candidates
        )

    def _create_candidates(
        self,
    ) -> list[ProviderCandidate]:
        ai_config = (
            self._config.get_section("ai")
        )

        configured_providers = (
            ai_config.get(
                "providers",
                [],
            )
        )

        if not isinstance(
            configured_providers,
            list,
        ):
            configured_providers = []

        candidates: list[
            ProviderCandidate
        ] = []

        for provider_config in (
            configured_providers
        ):
            candidate = (
                self._create_candidate(
                    provider_config
                )
            )

            if candidate is not None:
                candidates.append(candidate)

        return candidates

    def _create_candidate(
        self,
        provider_config: Any,
    ) -> ProviderCandidate | None:
        if not isinstance(
            provider_config,
            dict,
        ):
            return None

        name = provider_config.get(
            "name"
        )

        enabled = provider_config.get(
            "enabled",
            True,
        )

        if (
            not isinstance(name, str)
            or not isinstance(enabled, bool)
            or not enabled
        ):
            return None

        normalized_name = (
            name.strip().lower()
        )

        if normalized_name == "gemini":
            return (
                self._create_gemini_candidate(
                    provider_config
                )
            )

        if normalized_name == "mock":
            return ProviderCandidate(
                name="mock",
                provider=MockAIProvider(),
            )

        return None

    def _create_gemini_candidate(
        self,
        provider_config: dict[str, Any],
    ) -> ProviderCandidate | None:
        api_key = self._get_gemini_api_key()

        if api_key is None:
            return None

        model = provider_config.get(
            "model",
            "gemini-2.5-flash",
        )

        if not isinstance(model, str):
            return None

        normalized_model = model.strip()

        if not normalized_model:
            return None

        provider = GeminiAIProvider(
            api_key=api_key,
            model=normalized_model,
        )

        return ProviderCandidate(
            name="gemini",
            provider=provider,
        )

    def _get_gemini_api_key(
        self,
    ) -> str | None:
        for variable_name in (
            "GOOGLE_API_KEY",
            "GEMINI_API_KEY",
        ):
            value = self._environ.get(
                variable_name
            )

            if (
                isinstance(value, str)
                and value.strip()
            ):
                return value.strip()

        return None