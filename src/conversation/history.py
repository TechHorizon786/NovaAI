"""
Conversation history management for NOVA AI.

This module stores and manages messages exchanged
between the user and the AI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Message:
    """
    Represents a single chat message.
    """

    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class ConversationHistory:
    """
    Stores all messages for a conversation session.
    """

    def __init__(self) -> None:
        self._messages: List[Message] = []

    def add_user_message(self, content: str) -> None:
        """
        Add a user message.
        """
        self._messages.append(
            Message(
                role="user",
                content=content
            )
        )

    def add_assistant_message(self, content: str) -> None:
        """
        Add an AI assistant message.
        """
        self._messages.append(
            Message(
                role="assistant",
                content=content
            )
        )

    def get_messages(self) -> List[Message]:
        """
        Return all messages.
        """
        return self._messages.copy()

    def clear(self) -> None:
        """
        Remove all messages.
        """
        self._messages.clear()

    def message_count(self) -> int:
        """
        Return total message count.
        """
        return len(self._messages)

    def to_dict(self) -> List[dict]:
        """
        Convert history into serializable format.
        """
        return [message.to_dict() for message in self._messages]