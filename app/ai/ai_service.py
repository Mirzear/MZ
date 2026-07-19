from app.ai.ai_provider import AIProvider
from app.ai.ai_response import AIResponse
from app.ai.conversation_manager import (
    ConversationManager,
)


class AIService:
    def __init__(
        self,
        provider: AIProvider,
        conversation: ConversationManager | None = None,
    ) -> None:
        if not isinstance(
            provider,
            AIProvider,
        ):
            raise TypeError(
                "provider debe cumplir el "
                "contrato AIProvider."
            )

        if (
            conversation is not None
            and not isinstance(
                conversation,
                ConversationManager,
            )
        ):
            raise TypeError(
                "conversation debe ser una "
                "instancia de "
                "ConversationManager o None."
            )

        self.provider = provider
        self.conversation = (
            conversation
            if conversation is not None
            else ConversationManager()
        )

    def ask(
        self,
        prompt: str,
    ) -> str:
        """
        Send a prompt and return user-facing text.

        This method preserves compatibility with
        the original AIService API.
        """
        response = self.request(prompt)

        return response.to_user_text()

    def request(
        self,
        prompt: str,
        *,
        store_exchange: bool = True,
    ) -> AIResponse:
        """
        Send a prompt and return a structured
        AIResponse.
        """
        if not isinstance(
            store_exchange,
            bool,
        ):
            return AIResponse.from_error(
                "store_exchange debe ser "
                "booleano."
            )

        cleaned_prompt = self._normalize_prompt(
            prompt
        )

        if cleaned_prompt is None:
            if not isinstance(prompt, str):
                return AIResponse.from_error(
                    "La consulta debe ser una "
                    "cadena de caracteres."
                )

            return AIResponse.from_error(
                "No recibí ninguna consulta."
            )

        context = (
            self.conversation.get_messages()
        )

        try:
            response = (
                self.provider.generate_response(
                    prompt=cleaned_prompt,
                    context=context,
                )
            )
        except Exception as error:
            return AIResponse.from_error(
                "No pude obtener una respuesta "
                f"de la IA: {error}"
            )

        if not isinstance(
            response,
            AIResponse,
        ):
            return AIResponse.from_error(
                "El proveedor devolvió una "
                "respuesta inválida."
            )

        if (
            response.is_text
            and store_exchange
        ):
            self.record_completed_exchange(
                prompt=cleaned_prompt,
                response=response,
            )

        return response

    def record_completed_exchange(
        self,
        *,
        prompt: str,
        response: AIResponse,
    ) -> None:
        cleaned_prompt = self._normalize_prompt(
            prompt
        )

        if cleaned_prompt is None:
            raise ValueError(
                "No se puede guardar una "
                "consulta vacía o inválida."
            )

        if not isinstance(
            response,
            AIResponse,
        ):
            raise TypeError(
                "response debe ser una "
                "instancia de AIResponse."
            )

        if not response.is_text:
            raise ValueError(
                "Solo se pueden guardar "
                "respuestas de texto completas."
            )

        if response.content is None:
            raise ValueError(
                "La respuesta de texto no "
                "contiene contenido."
            )

        self.conversation.add_message(
            role="user",
            content=cleaned_prompt,
        )
        self.conversation.add_message(
            role="assistant",
            content=response.content,
        )

    def get_conversation(
        self,
    ) -> list[dict[str, str]]:
        return self.conversation.get_messages()

    def clear_conversation(self) -> None:
        self.conversation.clear()

    @staticmethod
    def _normalize_prompt(
        prompt: object,
    ) -> str | None:
        if not isinstance(prompt, str):
            return None

        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            return None

        return cleaned_prompt