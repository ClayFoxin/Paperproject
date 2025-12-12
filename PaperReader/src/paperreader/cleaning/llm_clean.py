"""LLM-assisted cleanup for XML when rule-based stripping yields nothing."""
from __future__ import annotations

import json
from typing import Any, Dict

from paperreader.llm.client import LLMClient
from paperreader.llm.prompts import build_cleaning_prompt
from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def clean_with_llm(client: LLMClient, raw_xml: str) -> Dict[str, Any]:
    """Use the configured LLM to pull narrative content out of XML."""
    if not raw_xml.strip():
        return {"text": "", "tables": [], "figures": []}

    prompt = build_cleaning_prompt(raw_xml)
    response = client.chat(prompt)

    try:
        parsed = json.loads(response) if isinstance(response, str) else {}
        if isinstance(parsed, dict):
            return {
                "text": parsed.get("text", ""),
                "tables": parsed.get("tables", []),
                "figures": parsed.get("figures", []),
            }
    except json.JSONDecodeError:
        logger.warning("LLM cleaning response not JSON; using raw text fallback")

    return {"text": response or raw_xml, "tables": [], "figures": []}
