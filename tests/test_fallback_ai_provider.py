import unittest

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)
from app.ai.ai_response import AIResponse
from app.ai.fallback_ai_provider import (
    FallbackAIProvider,
)
from app.ai.provider_candidate import (
    ProviderCandidate,
)


class SuccessfulProvider:

    def __init__(
        self,
        response_text: str,
    ) -> None:
        self.response_text = response_text
        self.calls = 0
        self.last_prompt: str | None = None
        self.last_context: (
            list[dict[str, str]] | None
        ) = None

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        self.calls += 1
        self.last_prompt = prompt
        self.last_context = context

        return AIResponse.from_text(
            self.response_text
        )


class FailingProvider:

    def __init__(
        self,
        error: AIProviderError,
    ) -> None:
        self.error = error
        self.calls = 0

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        self.calls += 1
        raise self.error


class UnexpectedErrorProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        raise RuntimeError(
            "Error inesperado"
        )


class FakeClock:

    def __init__(self) -> None:
        self.current_time = 0.0

    def __call__(self) -> float:
        return self.current_time

    def advance(
        self,
        seconds: float,
    ) -> None:
        self.current_time += seconds


class TestFallbackAIProvider(
    unittest.TestCase
):

    def test_uses_first_provider(
        self,
    ) -> None:
        first = SuccessfulProvider(
            "Respuesta principal"
        )
        second = SuccessfulProvider(
            "Respuesta secundaria"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ]
        )

        response = provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertEqual(
            response.content,
            "Respuesta principal",
        )
        self.assertEqual(
            first.calls,
            1,
        )
        self.assertEqual(
            second.calls,
            0,
        )

    def test_falls_back_after_recoverable_error(
        self,
    ) -> None:
        first = FailingProvider(
            AIProviderError(
                "Cuota agotada.",
                kind=(
                    AIProviderErrorKind
                    .QUOTA_EXHAUSTED
                ),
                provider_name="first",
            )
        )
        second = SuccessfulProvider(
            "Respuesta secundaria"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ]
        )

        response = provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertEqual(
            response.content,
            "Respuesta secundaria",
        )
        self.assertEqual(
            first.calls,
            1,
        )
        self.assertEqual(
            second.calls,
            1,
        )

    def test_passes_prompt_and_context(
        self,
    ) -> None:
        successful = SuccessfulProvider(
            "Respuesta"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="provider",
                    provider=successful,
                )
            ]
        )

        context = [
            {
                "role": "user",
                "content": "Anterior",
            }
        ]

        provider.generate_response(
            prompt="Consulta",
            context=context,
        )

        self.assertEqual(
            successful.last_prompt,
            "Consulta",
        )
        self.assertIs(
            successful.last_context,
            context,
        )

    def test_non_recoverable_error_stops_fallback(
        self,
    ) -> None:
        first = FailingProvider(
            AIProviderError(
                "Credenciales inválidas.",
                kind=(
                    AIProviderErrorKind
                    .AUTHENTICATION
                ),
                provider_name="first",
            )
        )
        second = SuccessfulProvider(
            "No debe ejecutarse"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ]
        )

        with self.assertRaises(
            AIProviderError
        ):
            provider.generate_response(
                prompt="Hola",
                context=[],
            )

        self.assertEqual(
            second.calls,
            0,
        )

    def test_unexpected_error_stops_fallback(
        self,
    ) -> None:
        second = SuccessfulProvider(
            "No debe ejecutarse"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=(
                        UnexpectedErrorProvider()
                    ),
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ]
        )

        with self.assertRaises(
            RuntimeError
        ):
            provider.generate_response(
                prompt="Hola",
                context=[],
            )

        self.assertEqual(
            second.calls,
            0,
        )

    def test_provider_in_cooldown_is_skipped(
        self,
    ) -> None:
        clock = FakeClock()

        first = FailingProvider(
            AIProviderError(
                "Límite alcanzado.",
                kind=(
                    AIProviderErrorKind
                    .RATE_LIMIT
                ),
                cooldown_seconds=60,
            )
        )
        second = SuccessfulProvider(
            "Respuesta secundaria"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ],
            clock=clock,
        )

        provider.generate_response(
            prompt="Primera",
            context=[],
        )

        provider.generate_response(
            prompt="Segunda",
            context=[],
        )

        self.assertEqual(
            first.calls,
            1,
        )
        self.assertEqual(
            second.calls,
            2,
        )

    def test_provider_is_retried_after_cooldown(
        self,
    ) -> None:
        clock = FakeClock()

        first = FailingProvider(
            AIProviderError(
                "Límite alcanzado.",
                kind=(
                    AIProviderErrorKind
                    .RATE_LIMIT
                ),
                cooldown_seconds=60,
            )
        )
        second = SuccessfulProvider(
            "Respuesta secundaria"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ],
            clock=clock,
        )

        provider.generate_response(
            prompt="Primera",
            context=[],
        )

        clock.advance(60)

        provider.generate_response(
            prompt="Segunda",
            context=[],
        )

        self.assertEqual(
            first.calls,
            2,
        )

    def test_disabled_provider_is_skipped(
        self,
    ) -> None:
        disabled = SuccessfulProvider(
            "No debe ejecutarse"
        )
        enabled = SuccessfulProvider(
            "Respuesta válida"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="disabled",
                    provider=disabled,
                    enabled=False,
                ),
                ProviderCandidate(
                    name="enabled",
                    provider=enabled,
                ),
            ]
        )

        response = provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertEqual(
            response.content,
            "Respuesta válida",
        )
        self.assertEqual(
            disabled.calls,
            0,
        )

    def test_reports_available_providers(
        self,
    ) -> None:
        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="gemini",
                    provider=SuccessfulProvider(
                        "Gemini"
                    ),
                ),
                ProviderCandidate(
                    name="groq",
                    provider=SuccessfulProvider(
                        "Groq"
                    ),
                    enabled=False,
                ),
            ]
        )

        self.assertEqual(
            provider
            .get_available_provider_names(),
            ["gemini"],
        )

    def test_clear_cooldowns(
        self,
    ) -> None:
        clock = FakeClock()

        first = FailingProvider(
            AIProviderError(
                "Timeout.",
                kind=(
                    AIProviderErrorKind.TIMEOUT
                ),
                cooldown_seconds=60,
            )
        )
        second = SuccessfulProvider(
            "Respuesta secundaria"
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ],
            clock=clock,
        )

        provider.generate_response(
            prompt="Primera",
            context=[],
        )

        provider.clear_cooldowns()

        provider.generate_response(
            prompt="Segunda",
            context=[],
        )

        self.assertEqual(
            first.calls,
            2,
        )

    def test_all_providers_fail(
        self,
    ) -> None:
        first = FailingProvider(
            AIProviderError(
                "Timeout.",
                kind=(
                    AIProviderErrorKind.TIMEOUT
                ),
            )
        )
        second = FailingProvider(
            AIProviderError(
                "Sin servicio.",
                kind=(
                    AIProviderErrorKind
                    .SERVICE_UNAVAILABLE
                ),
            )
        )

        provider = FallbackAIProvider(
            providers=[
                ProviderCandidate(
                    name="first",
                    provider=first,
                ),
                ProviderCandidate(
                    name="second",
                    provider=second,
                ),
            ]
        )

        with self.assertRaises(
            AIProviderError
        ) as context:
            provider.generate_response(
                prompt="Hola",
                context=[],
            )

        self.assertEqual(
            context.exception.kind,
            (
                AIProviderErrorKind
                .SERVICE_UNAVAILABLE
            ),
        )

    def test_rejects_duplicate_names(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            FallbackAIProvider(
                providers=[
                    ProviderCandidate(
                        name="provider",
                        provider=(
                            SuccessfulProvider(
                                "Uno"
                            )
                        ),
                    ),
                    ProviderCandidate(
                        name="PROVIDER",
                        provider=(
                            SuccessfulProvider(
                                "Dos"
                            )
                        ),
                    ),
                ]
            )


if __name__ == "__main__":
    unittest.main()