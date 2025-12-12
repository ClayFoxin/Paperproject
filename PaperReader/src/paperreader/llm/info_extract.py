"""High-level information extraction (materials/process/performance/novelty)."""
from __future__ import annotations

import json
from typing import Dict

from paperreader.llm.client import LLMClient
from paperreader.llm.prompts import build_info_prompt
from paperreader.llm.schemas import InfoExtraction
from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def extract_info(client: LLMClient, cleaned_doc: Dict) -> InfoExtraction:
    prompt = build_info_prompt(cleaned_doc.get("text", ""))
    response_text = client.chat(prompt)
    try:
        parsed = json.loads(response_text)
        return InfoExtraction(
            material_system=parsed.get("材料体系") or parsed.get("material_system"),
            process=parsed.get("工艺") or parsed.get("process"),
            performance=parsed.get("性能") or parsed.get("performance"),
            novelty=parsed.get("创新点") or parsed.get("novelty"),
        )
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response, returning stub info")
        return InfoExtraction(material_system=None, process=None, performance=None, novelty=None)
