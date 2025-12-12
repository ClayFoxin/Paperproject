"""Wrapper around OpenAI-compatible chat completion API."""
from __future__ import annotations

from typing import List, Optional

import httpx
from openai import OpenAI

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Thin wrapper that can operate in real or stub mode."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.stub = api_key is None
        if self.stub:
            self._client = None
            logger.warning("LLM client initialized in stub mode (no API key provided)")
        else:
            timeout_client = httpx.Client(timeout=60)
            self._client = OpenAI(api_key=api_key, base_url=base_url, http_client=timeout_client)

    def chat(self, messages: List[dict], temperature: float = 0.2) -> str:
        """Send chat messages and return the content string."""
        if self.stub:
            logger.info("Stub LLM response returned")
            return "{\"note\": \"LLM stub response; please configure OPENAI_API_KEY.\"}"

        response = self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=messages,
        )
        return response.choices[0].message.content or ""
