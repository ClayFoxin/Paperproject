"""Data schemas for LLM outputs."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class InfoExtraction:
    material_system: Optional[str] = None
    process: Optional[str] = None
    performance: Optional[str] = None
    novelty: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DataRecord:
    field: str
    value: Optional[str]
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
