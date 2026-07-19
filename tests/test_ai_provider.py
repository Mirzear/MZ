import unittest

from app.ai.ai_provider import AIProvider
from app.ai.ai_response import AIResponse


class ValidProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        return AIResponse.from_text(
            prompt
        )


class InvalidProvider:
    pass


class TestAIProvider(unittest.TestCase):

    def test_valid_provider_matches_protocol(
        self,
    ) -> None:
        provider = ValidProvider()

        self.assertIsInstance(
            provider,
            AIProvider,
        )

    def test_invalid_provider_does_not_match_protocol(
        self,
    ) -> None:
        provider = InvalidProvider()

        self.assertNotIsInstance(
            provider,
            AIProvider,
        )


if __name__ == "__main__":
    unittest.main()