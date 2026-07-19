from app.ai.ai_provider import AIProvider
from app.ai.ai_response import AIResponse
from app.ai.conversation_manager import (
    ConversationManager,
)


class AIService:

    def __init__(
        self,
        provider: AIProvider,
        conversation: (
            ConversationManager | None
        ) = None,
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
    ) -> AIResponse:
        """
        Send a prompt and return a structured
        AIResponse.
        """
        if not isinstance(
            prompt,
            str,
        ):
            return AIResponse.from_error(
                "La consulta debe ser una cadena "
                "de caracteres."
            )

        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
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

        if response.is_text:
            self._store_completed_exchange(
                prompt=cleaned_prompt,
                response=response,
            )

        return response

    def get_conversation(
        self,
    ) -> list[dict[str, str]]:
        return self.conversation.get_messages()

    def clear_conversation(self) -> None:
        self.conversation.clear()

    def _store_completed_exchange(
        self,
        prompt: str,
        response: AIResponse,
    ) -> None:
        if response.content is None:
            return

        self.conversation.add_message(
            role="user",
            content=prompt,
        )

        self.conversation.add_message(
            role="assistant",
            content=response.content,
        )