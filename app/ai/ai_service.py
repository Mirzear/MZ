from typing import Protocol


class AIProvider(Protocol):

    def generate_response(self, prompt: str) -> str:
        """Generate a response from a prompt."""
        ...


class AIService:

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def ask(self, prompt: str) -> str:
        """Send a prompt to the configured AI provider."""
        cleaned_prompt = prompt.strip()

        if not cleaned_prompt:
            return "No recibí ninguna consulta."

        return self.provider.generate_response(cleaned_prompt)