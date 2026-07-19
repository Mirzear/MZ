from app.ai.ai_response import AIResponse


class MockAIProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> AIResponse:
        """
        Generate a deterministic structured
        simulated response.
        """
        previous_messages = len(context)

        content = (
            f"Respuesta simulada de IA para: "
            f"{prompt} "
            f"[contexto previo: "
            f"{previous_messages} mensajes]"
        )

        return AIResponse.from_text(
            content
        )