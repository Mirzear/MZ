from typing import Protocol

from app.ai.conversation_manager import ConversationManager


class AIProvider(Protocol):

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> str:
        """Generate a response using the supplied context."""
        ...


class AIService:

    def __init__(
        self,
        provider: AIProvider,
        conversation: ConversationManager | None = None,
    ) -> None:
        self.provider = provider
        self.conversation = (
            conversation
            if conversation is not None
            else ConversationManager()
        )

    def ask(self, prompt: str) -> str:
        """Send a prompt to the configured AI provider."""
        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            return "No recibí ninguna consulta."

        context = self.conversation.get_messages()

        response = self.provider.generate_response(
            prompt=cleaned_prompt,
            context=context,
        )

        self.conversation.add_message(
            role="user",
            content=cleaned_prompt,
        )

        self.conversation.add_message(
            role="assistant",
            content=response,
        )

        return response

    def get_conversation(
        self,
    ) -> list[dict[str, str]]:
        return self.conversation.get_messages()

    def clear_conversation(self) -> None:
        self.conversation.clear()