"""Chat manager for NOVA AI."""

from ai.ai_engine import AIEngine
from core.command_router import CommandRouter


class ChatManager:
    """Handles chat messages independently of the UI."""

    def __init__(self) -> None:
        """Initialize the chat manager."""

        self._command_router = CommandRouter()
        self._ai_engine = AIEngine()

    def get_response(self, message: str) -> str:
        """
        Process the user message and return a response.
        """

        message = message.strip()

        if not message:
            return ""

        command_response = self._command_router.route(message)

        if command_response is not None:
            return command_response

        return self._ai_engine.generate_response(message)