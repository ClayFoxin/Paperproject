"""Remove metadata from parsed documents, keeping body/tables/figures."""
from __future__ import annotations

from typing import Any, Dict, List


METADATA_KEYS = {"metadata", "title", "authors", "references", "affiliations", "doi", "journal"}


def _concat_sections(sections: List[Dict[str, Any]]) -> str:
    blocks = []
    for section in sections:
        heading = section.get("heading")
        text = section.get("text", "")
        if heading:
            blocks.append(f"# {heading}\n{text}" if text else f"# {heading}")
        elif text:
            blocks.append(text)
    return "\n\n".join(blocks)


def strip_metadata(document: Dict[str, Any]) -> Dict[str, Any]:
    """Remove common metadata fields and retain narrative + structured artifacts."""
    content = document.get("content", {}) if isinstance(document, dict) else {}
    sections = content.get("sections", []) if isinstance(content, dict) else []
    cleaned = {
        "text": _concat_sections(sections),
        "tables": content.get("tables", []),
        "figures": content.get("figures", []),
    }
    return cleaned
