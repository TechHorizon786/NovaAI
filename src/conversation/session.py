"""
Session model for NOVA AI.

This module defines the ConversationSession object which stores
basic metadata about an active conversation.
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ConversationSession:
    """
    Represents a single conversation session.

    Every new chat receives its own unique session ID.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0

    def touch(self) -> None:
        """
        Update the last activity timestamp.
        """
        self.updated_at = datetime.now()

    def increment_message_count(self) -> None:
        """
        Increase the number of messages in this session.
        """
        self.message_count += 1
        self.touch()

    def rename(self, title: str) -> None:
        """
        Rename the conversation.
        """
        if title.strip():
            self.title = title.strip()
            self.touch()

    def to_dict(self) -> dict:
        """
        Convert the session to a serializable dictionary.
        """
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": self.message_count,
        }