from typing import Protocol, runtime_checkable

from app.ai.ai_response import AIResponse


@runtime_checkable
class AIProvider(Protocol):

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        """Generate a structured AI response."""
        ...