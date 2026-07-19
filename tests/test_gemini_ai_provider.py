import unittest

import httpx
from google.genai import errors, types

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
from app.ai.gemini_turn_state import (
    GeminiTurnState,
)
from app.tools.tool_call import ToolCall
from app.tools.tool_metadata import (
    ToolMetadata,
    ToolRiskLevel,
)


class FakeCandidate:
    def __init__(
        self,
        content: types.Content,
    ) -> None:
        self.content = content


class FakeFunctionCall:
    def __init__(
        self,
        *,
        name: object,
        args: object,
    ) -> None:
        self.name = name
        self.args = args


class FakeGeminiResponse:
    def __init__(
        self,
        text: str | None = None,
        function_calls: object = None,
        candidates: object = None,
    ) -> None:
        self.text = text
        self.function_calls = function_calls
        self.candidates = candidates


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
        self.last_config: object | None = None

    def generate_content(
        self,
        *,
        model: str,
        contents: list,
        config: object | None = None,
    ) -> object:
        self.calls += 1
        self.last_model = model
        self.last_contents = contents
        self.last_config = config

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
        tools: tuple[ToolMetadata, ...] = (),
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
            tools=tools,
            client=client,
        )

        return provider, models

    @staticmethod
    def _create_tool_metadata(
    ) -> ToolMetadata:
        return ToolMetadata(
            name="count_words",
            description=(
                "Cuenta las palabras de un texto."
            ),
            parameters={
                "text": {
                    "type": "string",
                    "description": (
                        "Texto que será analizado."
                    ),
                    "required": True,
                }
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def _create_tool_response(
        self,
        *,
        name: str,
        args: dict[str, object] | None,
    ) -> FakeGeminiResponse:
        model_content = types.Content(
            role="model",
            parts=[
                types.Part.from_function_call(
                    name=name,
                    args=args or {},
                )
            ],
        )

        return FakeGeminiResponse(
            function_calls=[
                FakeFunctionCall(
                    name=name,
                    args=args,
                )
            ],
            candidates=[
                FakeCandidate(
                    content=model_content,
                )
            ],
        )

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
                " Respuesta "
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

    def test_returns_tool_call_response(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=self._create_tool_response(
                name="count_words",
                args={
                    "text": "Hola mundo",
                },
            )
        )

        response = provider.generate_response(
            prompt="Contá las palabras",
            context=[],
        )

        self.assertTrue(
            response.is_tool_call
        )
        self.assertIsNotNone(
            response.tool_call
        )
        self.assertEqual(
            response.tool_call.tool_name,
            "count_words",
        )
        self.assertEqual(
            response.tool_call.arguments,
            {
                "text": "Hola mundo",
            },
        )

    def test_tool_call_accepts_missing_arguments(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=self._create_tool_response(
                name="get_current_datetime",
                args=None,
            )
        )

        response = provider.generate_response(
            prompt="¿Qué hora es?",
            context=[],
        )

        self.assertTrue(
            response.is_tool_call
        )
        self.assertIsNotNone(
            response.tool_call
        )
        self.assertEqual(
            response.tool_call.tool_name,
            "get_current_datetime",
        )
        self.assertEqual(
            response.tool_call.arguments,
            {},
        )

    def test_tool_call_contains_turn_state(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=self._create_tool_response(
                name="count_words",
                args={
                    "text": "Hola mundo",
                },
            )
        )

        response = provider.generate_response(
            prompt="Contá las palabras",
            context=[],
        )

        self.assertTrue(
            response.is_tool_call
        )
        self.assertIsInstance(
            response.provider_state,
            GeminiTurnState,
        )

        expected_contents = (
            provider._build_contents(
            prompt="Contá las palabras",
            context=[],
            )
        )

        self.assertEqual(
            response.provider_state.contents,
            tuple(expected_contents),
        )

        self.assertIsInstance(
            response.provider_state.model_content,
            types.Content,
        )

    

    def test_rejects_multiple_tool_calls(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                function_calls=[
                    FakeFunctionCall(
                        name="tool_one",
                        args={},
                    ),
                    FakeFunctionCall(
                        name="tool_two",
                        args={},
                    ),
                ]
            )
        )

        with self.assertRaises(
            AIProviderError
        ) as context:
            provider.generate_response(
                prompt="Ejecutá herramientas",
                context=[],
            )

        self.assertEqual(
            context.exception.kind,
            (
                AIProviderErrorKind
                .INVALID_RESPONSE
            ),
        )

    def test_rejects_tool_call_without_name(
        self,
    ) -> None:
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                function_calls=[
                    FakeFunctionCall(
                        name=" ",
                        args={},
                    )
                ]
            )
        )

        with self.assertRaises(
            AIProviderError
        ):
            provider.generate_response(
                prompt="Ejecutá",
                context=[],
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

    def test_does_not_send_tool_config_without_tools(
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

        self.assertIsNone(
            models.last_config
        )

    def test_sends_tool_declarations(
        self,
    ) -> None:
        metadata = (
            self._create_tool_metadata()
        )
        provider, models = (
            self._create_provider(
                response=FakeGeminiResponse(
                    "Respuesta"
                ),
                tools=(metadata,),
            )
        )

        provider.generate_response(
            prompt="Hola",
            context=[],
        )

        config = models.last_config

        self.assertIsNotNone(config)
        self.assertEqual(
            len(config.tools),
            1,
        )

        declarations = (
            config.tools[0]
            .function_declarations
        )

        self.assertEqual(
            len(declarations),
            1,
        )
        self.assertEqual(
            declarations[0].name,
            "count_words",
        )

        schema = (
            declarations[0]
            .parameters_json_schema
        )

        self.assertEqual(
            schema["type"],
            "object",
        )
        self.assertEqual(
            schema["required"],
            ["text"],
        )
        self.assertEqual(
            schema["properties"]["text"][
                "type"
            ],
            "string",
        )

    def test_tools_property_returns_metadata(
        self,
    ) -> None:
        metadata = (
            self._create_tool_metadata()
        )
        provider, _ = self._create_provider(
            response=FakeGeminiResponse(
                "Respuesta"
            ),
            tools=(metadata,),
        )

        self.assertEqual(
            provider.tools,
            (metadata,),
        )

    def test_rejects_invalid_tools(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            GeminiAIProvider(
                api_key="test-api-key",
                model="test-model",
                tools=(
                    object(),  # type: ignore[arg-type]
                ),
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
                    "content": (
                        "Pregunta anterior"
                    ),
                },
                {
                    "role": "assistant",
                    "content": (
                        "Respuesta anterior"
                    ),
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
            response=FakeGeminiResponse(" ")
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
            AIProviderErrorKind.RATE_LIMIT,
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
        with self.assertRaises(ValueError):
            GeminiAIProvider(
                api_key=" ",
                model="test-model",
            )

    def test_rejects_empty_model(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            GeminiAIProvider(
                api_key="test-api-key",
                model=" ",
            )


if __name__ == "__main__":
    unittest.main()