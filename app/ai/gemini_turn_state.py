from dataclasses import dataclass

from google.genai import types


@dataclass(frozen=True, slots=True)
class GeminiTurnState:
    model_content: types.Content