import unittest

from app.ai.ai_response import AIResponse
from app.ai.provider_candidate import (
    ProviderCandidate,
)


class ValidProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        return AIResponse.from_text(
            prompt
        )


class TestProviderCandidate(
    unittest.TestCase
):

    def test_creates_candidate(
        self,
    ) -> None:
        provider = ValidProvider()

        candidate = ProviderCandidate(
            name="gemini",
            provider=provider,
        )

        self.assertEqual(
            candidate.name,
            "gemini",
        )
        self.assertIs(
            candidate.provider,
            provider,
        )
        self.assertTrue(
            candidate.enabled
        )

    def test_normalizes_name(
        self,
    ) -> None:
        candidate = ProviderCandidate(
            name="  GEMINI  ",
            provider=ValidProvider(),
        )

        self.assertEqual(
            candidate.name,
            "gemini",
        )

    def test_accepts_disabled_candidate(
        self,
    ) -> None:
        candidate = ProviderCandidate(
            name="gemini",
            provider=ValidProvider(),
            enabled=False,
        )

        self.assertFalse(
            candidate.enabled
        )

    def test_rejects_empty_name(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            ProviderCandidate(
                name="   ",
                provider=ValidProvider(),
            )

    def test_rejects_invalid_provider(
        self,
    ) -> None:
        with self.assertRaises(
            TypeError
        ):
            ProviderCandidate(
                name="invalid",
                provider=object(),
            )


if __name__ == "__main__":
    unittest.main()