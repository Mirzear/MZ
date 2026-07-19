from collections.abc import Iterator
from typing import Protocol, runtime_checkable

from app.ai.ai_stream_event import (
    AIStreamEvent,
)


@runtime_checkable
class StreamingAIProvider(Protocol):

    def stream_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> Iterator[AIStreamEvent]:
        """
        Generate an AI response incrementally.

        The stream must finish with exactly one
        completed event containing the final
        structured AIResponse.
        """
        ...