from typing import Protocol

import httpx
from google import genai
from google.genai import errors, types

from app.ai.ai_provider_error import (
    AIProviderError,
    AIProviderErrorKind,
)
from app.ai.ai_response import AIResponse


class GeminiModelsClient(Protocol):

    def generate_content(
        self,
        *,
        model: str,
        contents: list[types.Content],
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
        client: GeminiClient | None = None,
    ) -> None:
        self._api_key = self._normalize_required_text(
            value=api_key,
            field_name="api_key",
        )
        self._model = self._normalize_required_text(
            value=model,
            field_name="model",
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

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        contents = self._build_contents(
            prompt=prompt,
            context=context,
        )

        try:
            response = (
                self._client.models
                .generate_content(
                    model=self._model,
                    contents=contents,
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
                "sin contenido de texto.",
                kind=(
                    AIProviderErrorKind
                    .INVALID_RESPONSE
                ),
                provider_name="gemini",
            )

        cleaned_response = response_text.strip()

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
            content = message.get("content")

            if (
                role not in {
                    "user",
                    "assistant",
                }
                or not isinstance(content, str)
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
                            text=content.strip()
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
            kind = self._classify_limit_error(
                normalized_error_text
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

        return AIProviderErrorKind.RATE_LIMIT

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