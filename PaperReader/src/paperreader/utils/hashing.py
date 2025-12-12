"""Utilities for stable hashing of documents/rows."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Union


Hashable = Union[str, bytes, Path]


def sha256_from_iterable(values: Iterable[Hashable]) -> str:
    """Compute a stable SHA256 hash from multiple values."""
    digest = hashlib.sha256()
    for value in values:
        if isinstance(value, Path):
            value = str(value)
        if isinstance(value, str):
            value = value.encode("utf-8")
        digest.update(value)
    return digest.hexdigest()
