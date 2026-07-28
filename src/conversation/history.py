"""
Conversation history management for NOVA AI.

This module stores and manages messages exchanged
between the user and the AI.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List


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

    def __init__(self, max_messages: int = 20) -> None:
        self._messages: Deque[Message] = deque(maxlen=max_messages)

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message with the specified role.
        """
        self._messages.append(
            Message(
                role=role,
                content=content
            )
        )

    def add_user_message(self, content: str) -> None:
        """
        Add a user message.
        """
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """
        Add an AI assistant message.
        """
        self.add_message("assistant", content)

    def get_messages(self) -> List[Message]:
        """
        Return all messages.
        """
        return list(self._messages)

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """
        Return the most recent messages.
        """
        return list(self._messages)[-limit:]

    def clear(self) -> None:
        """
        Remove all messages.
        """
        self._messages.clear()

    def is_empty(self) -> bool:
        """
        Return True if the history is empty.
        """
        return len(self._messages) == 0

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