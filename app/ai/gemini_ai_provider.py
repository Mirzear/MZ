from collections.abc import Iterable
from typing import Protocol

import httpx
from google import genai
from google.genai import errors, types

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)
from app.ai.ai_response import AIResponse
from app.ai.gemini_tool_mapper import (
    GeminiToolMapper,
)
from app.ai.gemini_turn_state import (
    GeminiTurnState,
)
from app.tools.tool_call import ToolCall
from app.tools.tool_metadata import ToolMetadata
from app.tools.tool_execution_result import (
    ToolExecutionResult,
)


class GeminiModelsClient(Protocol):
    def generate_content(
        self,
        *,
        model: str,
        contents: list[types.Content],
        config: (
            types.GenerateContentConfig
            | None
        ) = None,
    ) -> object:
        ...


class GeminiClient(Protocol):
    models: GeminiModelsClient


class GeminiAIProvider:

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        tools: Iterable[ToolMetadata] = (),
        client: GeminiClient | None = None,
    ) -> None:
        self._api_key = (
            self._normalize_required_text(
                value=api_key,
                field_name="api_key",
            )
        )
        self._model = (
            self._normalize_required_text(
                value=model,
                field_name="model",
            )
        )
        self._tool_metadata = (
            self._normalize_tools(tools)
        )
        self._client: GeminiClient = (
            client
            if client is not None
            else genai.Client(
                api_key=self._api_key
            )
        )

    @property
    def model(self) -> str:
        return self._model

    @property
    def tools(
        self,
    ) -> tuple[ToolMetadata, ...]:
        return self._tool_metadata

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        contents = self._build_contents(
            prompt=prompt,
            context=context,
        )

        response = self._generate_content(
            contents=contents,
        )

        return self._extract_response(
            response=response,
            contents=contents,
        )
    
    def continue_from_tool_result(
        self,
        *,
        previous_response: AIResponse,
        tool_result: ToolExecutionResult,
    ) -> AIResponse:
        if not isinstance(
            previous_response,
            AIResponse,
        ):
            raise TypeError(
                "previous_response debe ser una "
                "instancia de AIResponse."
            )

        if not isinstance(
            tool_result,
            ToolExecutionResult,
        ):
            raise TypeError(
                "tool_result debe ser una instancia "
                "de ToolExecutionResult."
            )

        if (
            not previous_response.is_tool_call
            or previous_response.tool_call is None
        ):
            raise AIProviderError(
                "Gemini solo puede continuar desde "
                "una respuesta de herramienta.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_REQUEST
                ),
                provider_name="gemini",
            )

        turn_state = (
            previous_response.provider_state
        )

        if not isinstance(
            turn_state,
            GeminiTurnState,
        ):
            raise AIProviderError(
                "La respuesta anterior no contiene "
                "un estado válido de Gemini.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_REQUEST
                ),
                provider_name="gemini",
            )

        previous_tool_call = (
            previous_response.tool_call
        )

        if (
            previous_tool_call.tool_name
            != tool_result.tool_name
        ):
            raise AIProviderError(
                "El resultado recibido no pertenece "
                "a la herramienta solicitada por "
                "Gemini.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_REQUEST
                ),
                provider_name="gemini",
            )

        if (
            tool_result.call_id is not None
            and tool_result.call_id
            != previous_tool_call.call_id
        ):
            raise AIProviderError(
                "El resultado recibido no pertenece "
                "a la llamada de herramienta "
                "solicitada por Gemini.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_REQUEST
                ),
                provider_name="gemini",
            )

        function_response_content = (
            self._build_function_response_content(
                tool_result
            )
        )

        contents = [
            *turn_state.contents,
            turn_state.model_content,
            function_response_content,
        ]

        response = self._generate_content(
            contents=contents,
        )

        return self._extract_response(
            response=response,
            contents=contents,
        )

    def _generate_content(
        self,
        *,
        contents: list[types.Content],
    ) -> object:
        config = self._build_config()

        try:
            return (
                self._client.models
                .generate_content(
                    model=self._model,
                    contents=contents,
                    config=config,
                )
            )
        except errors.APIError as error:
            raise self._translate_api_error(
                error
            ) from error
        except httpx.TimeoutException as error:
            raise AIProviderError(
                "La solicitud a Gemini excedió "
                "el tiempo de espera.",
                kind=(
                    AIProviderErrorKind.TIMEOUT
                ),
                provider_name="gemini",
            ) from error
        except httpx.TransportError as error:
            raise AIProviderError(
                "No fue posible conectar con "
                "Gemini.",
                kind=(
                    AIProviderErrorKind.NETWORK
                ),
                provider_name="gemini",
            ) from error

    def _extract_response(
        self,
        *,
        response: object,
        contents: list[types.Content],
    ) -> AIResponse:
        function_call_response = (
            self._extract_function_call(
                response=response,
                contents=contents,
            )
        )

        if function_call_response is not None:
            return function_call_response

        return self._extract_text_response(
            response
        )

    def _build_config(
        self,
    ) -> (
        types.GenerateContentConfig
        | None
    ):
        gemini_tools = (
            GeminiToolMapper.build_tools(
                self._tool_metadata
            )
        )

        if not gemini_tools:
            return None

        return types.GenerateContentConfig(
            tools=gemini_tools,
        )

    def _extract_function_call(
         self,
        *,
        response: object,
        contents: list[types.Content],
    ) -> AIResponse | None:
        function_calls = getattr(
            response,
            "function_calls",
            None,
        )

        if function_calls is None:
            return None

        try:
            calls = list(function_calls)
        except TypeError as error:
            raise AIProviderError(
                "Gemini devolvió llamadas a "
                "herramientas inválidas.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            ) from error

        if not calls:
            return None

        if len(calls) > 1:
            raise AIProviderError(
                "Gemini solicitó varias "
                "herramientas simultáneamente, "
                "pero MZ todavía admite una "
                "llamada por respuesta.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        function_call = calls[0]

        function_name = getattr(
            function_call,
            "name",
            None,
        )
        function_arguments = getattr(
            function_call,
            "args",
            None,
        )

        if (
            not isinstance(
                function_name,
                str,
            )
            or not function_name.strip()
        ):
            raise AIProviderError(
                "Gemini devolvió una llamada "
                "sin nombre de herramienta.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        if function_arguments is None:
            function_arguments = {}

        if not isinstance(
            function_arguments,
            dict,
        ):
            try:
                function_arguments = dict(
                    function_arguments
                )
            except (
                TypeError,
                ValueError,
            ) as error:
                raise AIProviderError(
                    "Gemini devolvió argumentos "
                    "de herramienta inválidos.",
                    kind=(
                        AIProviderErrorKind
                        .INVALID_RESPONSE
                    ),
                    provider_name="gemini",
                ) from error

        return AIResponse.from_tool_call(
            ToolCall(
                tool_name=(
                    function_name.strip()
                ),
                arguments=(
                    function_arguments
                ),
            ),
            provider_state=(
                self._build_turn_state(
                    response=response,
                    contents=contents,
                )
            ),

            )

    def _build_turn_state(
        self,
        *,
        response: object,
        contents: list[types.Content],
    ) -> GeminiTurnState:
        candidates = getattr(
            response,
            "candidates",
            None,
        )

        if candidates is None:
            raise AIProviderError(
                "Gemini devolvió una llamada "
                "a herramienta sin contenido.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        try:
            candidate_list = list(
                candidates
            )
        except TypeError as error:
            raise AIProviderError(
                "Gemini devolvió candidatos "
                "inválidos para continuar "
                "el turno.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            ) from error

        if not candidate_list:
            raise AIProviderError(
                "Gemini devolvió una llamada "
                "a herramienta sin contenido.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        model_content = getattr(
            candidate_list[0],
            "content",
            None,
        )

        if not isinstance(
            model_content,
            types.Content,
        ):
            raise AIProviderError(
                "Gemini devolvió un contenido "
                "inválido para continuar "
                "el turno.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        return GeminiTurnState(
            contents=tuple(contents),
            model_content=model_content,
        )


    def _extract_text_response(
        self,
        response: object,
    ) -> AIResponse:
        response_text = getattr(
            response,
            "text",
            None,
        )

        if not isinstance(
            response_text,
            str,
        ):
            raise AIProviderError(
                "Gemini devolvió una respuesta "
                "sin texto ni llamada a una "
                "herramienta.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        cleaned_response = (
            response_text.strip()
        )

        if not cleaned_response:
            raise AIProviderError(
                "Gemini devolvió una respuesta "
                "de texto vacía.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        return AIResponse.from_text(
            cleaned_response
        )

    def _build_contents(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> list[types.Content]:
        contents: list[types.Content] = []

        for message in context:
            role = message.get("role")
            content = message.get(
                "content"
            )

            if (
                role not in {
                    "user",
                    "assistant",
                }
                or not isinstance(
                    content,
                    str,
                )
                or not content.strip()
            ):
                raise AIProviderError(
                    "El historial de conversación "
                    "contiene un mensaje inválido.",
                    kind=(
                        AIProviderErrorKind
                        .INVALID_REQUEST
                    ),
                    provider_name="gemini",
                )

            gemini_role = (
                "model"
                if role == "assistant"
                else "user"
            )

            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[
                        types.Part.from_text(
                            text=(
                                content.strip()
                            )
                        )
                    ],
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=prompt
                    )
                ],
            )
        )

        return contents

    def _translate_api_error(
        self,
        error: errors.APIError,
    ) -> AIProviderError:
        status_code = getattr(
            error,
            "code",
            None,
        )
        error_text = str(error)
        normalized_error_text = (
            error_text.lower()
        )

        if status_code in {401, 403}:
            kind = (
                AIProviderErrorKind
                .AUTHENTICATION
            )
            message = (
                "Gemini rechazó las credenciales "
                "configuradas."
            )
        elif status_code == 400:
            kind = (
                AIProviderErrorKind
                .INVALID_REQUEST
            )
            message = (
                "Gemini rechazó la solicitud "
                "enviada."
            )
        elif status_code == 408:
            kind = (
                AIProviderErrorKind.TIMEOUT
            )
            message = (
                "La solicitud a Gemini excedió "
                "el tiempo de espera."
            )
        elif status_code == 429:
            kind = (
                self._classify_limit_error(
                    normalized_error_text
                )
            )

            if (
                kind
                is AIProviderErrorKind
                .QUOTA_EXHAUSTED
            ):
                message = (
                    "Se agotó temporalmente la "
                    "cuota disponible de Gemini."
                )
            else:
                message = (
                    "Gemini recibió demasiadas "
                    "solicitudes."
                )
        elif status_code in {
            500,
            502,
            503,
        }:
            kind = (
                AIProviderErrorKind
                .SERVICE_UNAVAILABLE
            )
            message = (
                "El servicio de Gemini no está "
                "disponible temporalmente."
            )
        elif status_code == 504:
            kind = (
                AIProviderErrorKind.TIMEOUT
            )
            message = (
                "Gemini no respondió dentro del "
                "tiempo esperado."
            )
        else:
            kind = (
                AIProviderErrorKind.UNKNOWN
            )
            message = (
                "Gemini devolvió un error no "
                "reconocido."
            )

        return AIProviderError(
            message,
            kind=kind,
            provider_name="gemini",
        )

    @staticmethod
    def _build_function_response_content(
        tool_result: ToolExecutionResult,
    ) -> types.Content:
        if tool_result.succeeded:
            response_payload = {
                "result": tool_result.output,
            }
        else:
            response_payload = {
                "status": tool_result.status.value,
                "error": tool_result.error_message,
            }

        function_response_part = (
            types.Part.from_function_response(
                name=tool_result.tool_name,
                response=response_payload,
            )
        )

        return types.Content(
            role="tool",
            parts=[
                function_response_part,
            ],
        )

    @staticmethod
    def _classify_limit_error(
        error_text: str,
    ) -> AIProviderErrorKind:
        quota_indicators = {
            "quota",
            "resource_exhausted",
            "resource exhausted",
            "daily limit",
            "per day",
        }

        if any(
            indicator in error_text
            for indicator in quota_indicators
        ):
            return (
                AIProviderErrorKind
                .QUOTA_EXHAUSTED
            )

        return (
            AIProviderErrorKind.RATE_LIMIT
        )

    @staticmethod
    def _normalize_tools(
        tools: Iterable[ToolMetadata],
    ) -> tuple[ToolMetadata, ...]:
        try:
            normalized_tools = tuple(
                tools
            )
        except TypeError as error:
            raise TypeError(
                "tools debe ser un iterable de "
                "ToolMetadata."
            ) from error

        for metadata in normalized_tools:
            if not isinstance(
                metadata,
                ToolMetadata,
            ):
                raise TypeError(
                    "Cada herramienta debe ser "
                    "una instancia de "
                    "ToolMetadata."
                )

        return normalized_tools

    @staticmethod
    def _normalize_required_text(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} debe ser una "
                "cadena de caracteres."
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} no puede estar "
                "vacío."
            )

        return normalized_value