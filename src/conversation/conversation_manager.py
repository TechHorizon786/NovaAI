"""
Conversation manager for NOVA AI.

Coordinates the active conversation session,
message history, and context building.
"""

from conversation.session import ConversationSession
from conversation.history import ConversationHistory
from conversation.context_builder import ContextBuilder


class ConversationManager:
    """
    Main controller for a conversation.
    """

    def __init__(self) -> None:
        self.session = ConversationSession()
        self.history = ConversationHistory()
        self.context_builder = ContextBuilder()

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the conversation.
        """
        self.history.add_user_message(content)
        self.session.increment_message_count()

    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant message to the conversation.
        """
        self.history.add_assistant_message(content)
        self.session.increment_message_count()

    def get_context(self) -> list:
        """
        Return the latest conversation context.
        """
        return self.context_builder.build(
            self.history.get_messages()
        )

    def get_messages(self):
        """
        Return all conversation messages.
        """
        return self.history.get_messages()

    def get_recent_messages(self, limit: int = 10):
        """
        Return the most recent conversation messages.
        """
        return self.history.get_recent_messages(limit)

    def clear_conversation(self) -> None:
        """
        Reset the current conversation.
        """
        self.history.clear()
        self.session = ConversationSession()

    def get_session_info(self) -> dict:
        """
        Return session information.
        """
        return self.session.to_dict()

    def get_message_count(self) -> int:
        """
        Return the total number of messages.
        """
        return self.session.message_count

    def is_empty(self) -> bool:
        """
        Return True if the conversation is empty.
        """
        return self.history.is_empty()