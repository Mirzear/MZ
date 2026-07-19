import unittest

import httpx
from google.genai import errors

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)
from app.ai.ai_response import (
    AIResponse,
    AIResponseType,
)
from app.ai.gemini_ai_provider import (
    GeminiAIProvider,
)


class FakeGeminiResponse:

    def __init__(
        self,
        text: object,
    ) -> None:
        self.text = text


class FakeModelsClient:

    def __init__(
        self,
        *,
        response: object | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls = 0
        self.last_model: str | None = None
        self.last_contents: list | None = None

    def generate_content(
        self,
        *,
        model: str,
        contents: list,
    ) -> object:
        self.calls += 1
        self.last_model = model
        self.last_contents = contents

        if self.error is not None:
            raise self.error

        return self.response


class FakeGeminiClient:

    def __init__(
        self,
        models: FakeModelsClient,
    ) -> None:
        self.models = models


class TestGeminiAIProvider(
    unittest.TestCase
):

    def _create_provider(
        self,
        *,
        response: object | None = None,
        error: Exception | None = None,
    ) -> tuple[
        GeminiAIProvider,
        FakeModelsClient,
    ]:
        models = FakeModelsClient(
            response=response,
            error=error,
        )

        client = FakeGeminiClient(
            models=models
        )

        provider = GeminiAIProvider(
            api_key="test-api-key",
            model="test-model",
            client=client,
        )

        return provider, models

    def test_returns_structured_text_response(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                "Respuesta de Gemini"
            )
        )

        response = provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertIsInstance(
            response,
            AIResponse,
        )
        self.assertEqual(
            response.response_type,
            AIResponseType.TEXT,
        )
        self.assertEqual(
            response.content,
            "Respuesta de Gemini",
        )

    def test_cleans_response_text(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                "   Respuesta   "
            )
        )

        response = provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertEqual(
            response.content,
            "Respuesta",
        )

    def test_sends_configured_model(
        self,
    ) -> None:
        provider, models = (
            self._create_provider(
                response=FakeGeminiResponse(
                    "Respuesta"
                )
            )
        )

        provider.generate_response(
            prompt="Hola",
            context=[],
        )

        self.assertEqual(
            models.last_model,
            "test-model",
        )

    def test_converts_conversation_roles(
        self,
    ) -> None:
        provider, models = (
            self._create_provider(
                response=FakeGeminiResponse(
                    "Respuesta"
                )
            )
        )

        provider.generate_response(
            prompt="Pregunta actual",
            context=[
                {
                    "role": "user",
                    "content": "Pregunta anterior",
                },
                {
                    "role": "assistant",
                    "content": "Respuesta anterior",
                },
            ],
        )

        contents = models.last_contents

        self.assertIsNotNone(contents)
        self.assertEqual(
            len(contents),
            3,
        )
        self.assertEqual(
            contents[0].role,
            "user",
        )
        self.assertEqual(
            contents[1].role,
            "model",
        )
        self.assertEqual(
            contents[2].role,
            "user",
        )
        self.assertEqual(
            contents[2].parts[0].text,
            "Pregunta actual",
        )

    def test_invalid_context_raises_error(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                "Respuesta"
            )
        )

        with self.assertRaises(
            AIProviderError
        ) as context:
            provider.generate_response(
                prompt="Hola",
                context=[
                    {
                        "role": "system",
                        "content": "Mensaje",
                    }
                ],
            )

        self.assertEqual(
            context.exception.kind,
            (
                AIProviderErrorKind
                .INVALID_REQUEST
            ),
        )

    def test_empty_response_raises_error(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                "   "
            )
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
                .INVALID_RESPONSE
            ),
        )

    def test_missing_text_raises_error(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=object()
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
                .INVALID_RESPONSE
            ),
        )

    def test_authentication_error_is_translated(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            error=errors.ClientError(
                401,
                {
                    "message": (
                        "Invalid API key"
                    )
                },
                None,
            )
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
                .AUTHENTICATION
            ),
        )
        self.assertFalse(
            context.exception.fallback_allowed
        )

    def test_quota_error_is_translated(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            error=errors.ClientError(
                429,
                {
                    "message": (
                        "Quota exhausted"
                    )
                },
                None,
            )
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
                .QUOTA_EXHAUSTED
            ),
        )
        self.assertTrue(
            context.exception.fallback_allowed
        )

    def test_rate_limit_is_translated(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            error=errors.ClientError(
                429,
                {
                    "message": (
                        "Too many requests"
                    )
                },
                None,
            )
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
                .RATE_LIMIT
            ),
        )

    def test_service_error_is_translated(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            error=errors.ServerError(
                503,
                {
                    "message": (
                        "Service unavailable"
                    )
                },
                None,
            )
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

    def test_timeout_is_translated(
        self,
    ) -> None:
        request = httpx.Request(
            method="POST",
            url="https://example.com",
        )

        provider, _ = self._create_provider(
            error=httpx.ReadTimeout(
                "Timeout",
                request=request,
            )
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
            AIProviderErrorKind.TIMEOUT,
        )

    def test_network_error_is_translated(
        self,
    ) -> None:
        request = httpx.Request(
            method="POST",
            url="https://example.com",
        )

        provider, _ = self._create_provider(
            error=httpx.ConnectError(
                "Connection failed",
                request=request,
            )
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
            AIProviderErrorKind.NETWORK,
        )

    def test_rejects_empty_api_key(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            GeminiAIProvider(
                api_key="   ",
                model="test-model",
            )

    def test_rejects_empty_model(
        self,
    ) -> None:
        with self.assertRaises(
            ValueError
        ):
            GeminiAIProvider(
                api_key="test-api-key",
                model="   ",
            )


if __name__ == "__main__":
    unittest.main()