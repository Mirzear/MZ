import unittest

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)


class TestAIProviderError(
    unittest.TestCase
):

    def test_creates_provider_error(
        self,
    ) -> None:
        error = AIProviderError(
            "Límite alcanzado.",
            kind=(
                AIProviderErrorKind
                .RATE_LIMIT
            ),
            provider_name="Gemini",
        )

        self.assertEqual(
            error.message,
            "Límite alcanzado.",
        )
        self.assertEqual(
            error.provider_name,
            "gemini",
        )
        self.assertEqual(
            error.kind,
            AIProviderErrorKind.RATE_LIMIT,
        )

    def test_recoverable_error_allows_fallback(
        self,
    ) -> None:
        error = AIProviderError(
            "Timeout.",
            kind=(
                AIProviderErrorKind.TIMEOUT
            ),
        )

        self.assertTrue(
            error.fallback_allowed
        )

    def test_authentication_error_blocks_fallback(
        self,
    ) -> None:
        error = AIProviderError(
            "Credenciales inválidas.",
            kind=(
                AIProviderErrorKind
                .AUTHENTICATION
            ),
        )

        self.assertFalse(
            error.fallback_allowed
        )

    def test_uses_default_cooldown(
        self,
    ) -> None:
        error = AIProviderError(
            "Límite alcanzado.",
            kind=(
                AIProviderErrorKind
                .RATE_LIMIT
            ),
        )

        self.assertEqual(
            error.cooldown_seconds,
            60.0,
        )

    def test_accepts_custom_cooldown(
        self,
    ) -> None:
        error = AIProviderError(
            "Cuota agotada.",
            kind=(
                AIProviderErrorKind
                .QUOTA_EXHAUSTED
            ),
            cooldown_seconds=120,
        )

        self.assertEqual(
            error.cooldown_seconds,
            120.0,
        )

    def test_rejects_empty_message(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIProviderError(
                "   ",
                kind=(
                    AIProviderErrorKind
                    .UNKNOWN
                ),
            )

    def test_rejects_negative_cooldown(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            AIProviderError(
                "Error.",
                kind=(
                    AIProviderErrorKind
                    .NETWORK
                ),
                cooldown_seconds=-1,
            )

    def test_exception_text_includes_provider(
        self,
    ) -> None:
        error = AIProviderError(
            "Servicio no disponible.",
            kind=(
                AIProviderErrorKind
                .SERVICE_UNAVAILABLE
            ),
            provider_name="Groq",
        )

        self.assertEqual(
            str(error),
            (
                "[groq] Servicio no "
                "disponible."
            ),
        )


if __name__ == "__main__":
    unittest.main()