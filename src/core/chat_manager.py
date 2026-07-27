"""Chat manager for NOVA AI."""


class ChatManager:
    """Handles chat messages independently of the UI."""

    def get_response(self, message: str) -> str:
        """
        Process the user message and return a response.

        AI integration will be added in future versions.
        """

        message = message.strip()

        if not message:
            return ""

        return "AI integration coming soon..."