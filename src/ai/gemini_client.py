"""
Gemini client for NOVA AI.

This module is responsible for communicating with the
Google Gemini API.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google import genai


class GeminiClient:
    """Handles communication with the Gemini API."""

    def __init__(self) -> None:
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not found. Please configure your .env file."
            )

        self.client = genai.Client(api_key=api_key)

    def generate_response(self, message: str) -> str:
        """
        Generate a response from Gemini.
        """

        try:
            response = self.client.models.generate_content(
             model="gemini-3.6-flash",
                contents=message,
            )

            if response.text:
                return response.text.strip()

            return "No response returned from Gemini."

        except Exception as exc:
            return f"Gemini Error: {exc}"