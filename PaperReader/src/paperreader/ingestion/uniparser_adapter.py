"""Adapter to call Uni-parser or other parsers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


DEFAULT_PARSED_STRUCTURE = {
    "metadata": {"title": "", "authors": [], "doi": ""},
    "content": {"sections": [], "tables": [], "figures": []},
}


def parse_document(source: Path, output_path: Path, doi: Optional[str] = None) -> Dict[str, Any]:
    """Parse a document using Uni-parser (placeholder implementation)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        logger.warning("Source %s not found. Writing placeholder parsed JSON.", source)
        result = DEFAULT_PARSED_STRUCTURE.copy()
        result["metadata"]["doi"] = doi or ""
    else:
        # TODO: integrate real Uni-parser invocation
        logger.info("Pretending to parse %s via Uni-parser", source)
        result = DEFAULT_PARSED_STRUCTURE.copy()
        result["metadata"]["doi"] = doi or source.stem
        result["content"]["sections"] = [
            {"heading": "Introduction", "text": "Sample introduction content."},
            {"heading": "Methods", "text": "Sample methods content."},
        ]
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
