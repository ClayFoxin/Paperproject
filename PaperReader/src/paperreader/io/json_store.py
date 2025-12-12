"""Utility functions for JSON persistence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import ujson

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        ujson.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Saved JSON to %s", path)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        try:
            return ujson.load(f)
        except ValueError:
            f.seek(0)
            return json.load(f)
