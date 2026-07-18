class MockAIProvider:

    def generate_response(self, prompt: str) -> str:
        """Generate a simulated AI response."""
        return (
            "Respuesta simulada de IA para: "
            f"{prompt}"
        )