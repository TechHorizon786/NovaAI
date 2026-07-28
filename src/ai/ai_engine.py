"""
AI Engine implementation for NOVA AI.
"""

from __future__ import annotations

from ai.gemini_client import GeminiClient


class AIEngine:
    """
    Main AI Engine used by NOVA AI.

    This class acts as the bridge between the application
    and the configured AI provider.
    """

    def __init__(self) -> None:
        self._client = GeminiClient()

    def generate_response(self, prompt: str) -> str:
        """
        Generate an AI response.
        """

        prompt = prompt.strip()

        if not prompt:
            return ""

        return self._client.generate_response(prompt)