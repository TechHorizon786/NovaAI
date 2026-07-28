"""
Context builder for NOVA AI.

Builds the conversation context that will be sent
to the AI engine.
"""

from typing import List

from conversation.history import Message


class ContextBuilder:
    """
    Builds conversation context from chat history.
    """

    def __init__(self, max_messages: int = 10) -> None:
        self.max_messages = max_messages

    def build(self, messages: List[Message]) -> List[dict]:
        """
        Build context from the latest messages.

        Returns:
            List of dictionaries in the format expected
            by AI providers.
        """

        recent_messages = messages[-self.max_messages:]

        context = []

        for message in recent_messages:
            context.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        return context

    def set_max_messages(self, value: int) -> None:
        """
        Update the maximum number of messages
        included in the context.
        """

        if value > 0:
            self.max_messages = value