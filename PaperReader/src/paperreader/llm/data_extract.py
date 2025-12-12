"""Field-level data extraction driven by prompts."""
from __future__ import annotations

import json
from typing import Dict, List

from paperreader.llm.client import LLMClient
from paperreader.llm.prompts import build_data_prompt
from paperreader.llm.schemas import DataRecord
from paperreader.utils.log import get_logger

logger = get_logger(__name__)


DEFAULT_FIELDS = {
    "材料": "文中研究的材料或化学体系",
    "工艺": "使用的制备或处理方法",
    "性能": "关键性能指标数值或趋势",
}


def extract_data(client: LLMClient, cleaned_doc: Dict, fields: Dict[str, str] | None = None) -> List[DataRecord]:
    fields = fields or DEFAULT_FIELDS
    prompt = build_data_prompt(cleaned_doc.get("text", ""), fields)
    response_text = client.chat(prompt)
    try:
        parsed = json.loads(response_text)
        records = []
        for field, description in fields.items():
            value = parsed.get(field) if isinstance(parsed, dict) else None
            evidence = None
            if isinstance(value, dict):
                evidence = value.get("evidence")
                value = value.get("value")
            records.append(DataRecord(field=field, value=value, evidence=evidence))
        return records
    except json.JSONDecodeError:
        logger.warning("Failed to parse structured data, returning empty list")
        return [DataRecord(field=field, value=None, evidence=None) for field in fields]
