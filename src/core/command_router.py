"""Command routing interface for the NOVA AI application."""

from typing import Callable


class CommandRouter:
    """Routes recognized user commands to registered handlers."""

    def __init__(self) -> None:
        """Initialize the command router."""
        self._commands: dict[str, Callable[[], str]] = {}

    def register_command(
        self,
        command: str,
        handler: Callable[[], str],
    ) -> None:
        """Register a command and its handler."""
        normalized_command = command.strip().lower()

        if not normalized_command:
            raise ValueError("Command cannot be empty.")

        self._commands[normalized_command] = handler

    def route(self, message: str) -> str | None:
        """Route a message to a registered command handler."""
        normalized_message = message.strip().lower()

        if not normalized_message:
            return None

        handler = self._commands.get(normalized_message)

        if handler is None:
            return None

        return handler()