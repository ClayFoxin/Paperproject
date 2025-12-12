"""Adapter to call Uni-parser or other parsers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


DEFAULT_PARSED_STRUCTURE = {
    "metadata": {"title": "", "authors": [], "doi": ""},
    "content": {"sections": [], "tables": [], "figures": []},
}


def _fallback_structure(doi: Optional[str]) -> Dict[str, Any]:
    fallback = DEFAULT_PARSED_STRUCTURE.copy()
    fallback["metadata"]["doi"] = doi or ""
    return fallback


def parse_document(
    source: Path,
    output_path: Path,
    doi: Optional[str] = None,
    host: Optional[str] = None,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    """Parse a document using Uni-parser HTTP endpoint.

    If the remote call fails, a minimal placeholder structure is returned so
    downstream steps can continue.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        logger.warning("Source %s not found. Writing placeholder parsed JSON.", source)
        result = _fallback_structure(doi)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    base_host = host or "http://101.126.82.63:40001"
    effective_token = token or "article"
    trigger_url = f"{base_host}/trigger-file-async"
    result_url = f"{base_host}/get-result"

    data = {
        "token": effective_token,
        "sync": True,
        "textual": True,
        "chart": True,
        "table": True,
        "molecule": True,
        "equation": True,
        "figure": True,
        "expression": True,
    }

    try:
        with source.open("rb") as fh:
            response = requests.post(trigger_url, files={"file": fh}, data=data)
        trigger_resp = response.json()
    except Exception as exc:  # pragma: no cover - network/file errors
        logger.error("Uni-parser trigger failed for %s: %s", source, exc)
        result = _fallback_structure(doi)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    if trigger_resp.get("status") != "success":
        logger.error("Uni-parser returned non-success for %s: %s", source, trigger_resp)
        result = _fallback_structure(doi)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    result_req = {
        "token": effective_token,
        "content": True,
        "objects": True,
        "pages_dict": True,
    }

    try:
        result: Dict[str, Any] = requests.post(result_url, json=result_req).json()
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("Uni-parser result fetch failed for %s: %s", source, exc)
        result = _fallback_structure(doi)
    else:
        logger.info("Parsed %s via Uni-parser", source)
        if doi:
            result.setdefault("metadata", {}).setdefault("doi", doi)

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
