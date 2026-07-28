"""Chat manager for NOVA AI."""

from ai.ai_engine import AIEngine
from conversation.conversation_manager import ConversationManager
from core.command_router import CommandRouter


class ChatManager:
    """Handles chat messages independently of the UI."""

    def __init__(self) -> None:
        """Initialize the chat manager."""

        self._command_router = CommandRouter()
        self._conversation_manager = ConversationManager()
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

        # Store user message
        self._conversation_manager.add_user_message(message)

        # Build conversation context
        context = self._conversation_manager.get_context()

        # Generate AI response
        response = self._ai_engine.generate_response(context)

        # Store assistant response
        self._conversation_manager.add_assistant_message(response)

        return response

    def clear_conversation(self) -> None:
        """
        Clear the active conversation.
        """
        self._conversation_manager.clear_conversation()

    def get_message_count(self) -> int:
        """
        Return the total number of conversation messages.
        """
        return self._conversation_manager.get_message_count()