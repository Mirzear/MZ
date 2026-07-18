class MockAIProvider:

    def generate_response(
        self,
        prompt: str,
        context: list[dict[str, str]],
    ) -> str:
        """Generate a deterministic simulated response."""
        previous_messages = len(context)

        return (
            f"Respuesta simulada de IA para: {prompt} "
            f"[contexto previo: {previous_messages} mensajes]"
        )