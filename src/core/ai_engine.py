"""AI engine interface for the NOVA AI application."""


class AIEngine:
    """Base interface for future AI engine implementations."""

    def generate_response(self, message: str) -> str:
        """Generate a response for the provided user message."""
        raise NotImplementedError(
            "AI engine implementations must override generate_response()."
        )