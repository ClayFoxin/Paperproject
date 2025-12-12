"""Handle PDF uploads (local paths)."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def resolve_pdf(doi: str, pdf_dir: Path) -> Optional[Path]:
    """Return the path to a PDF matching the DOI if present."""
    normalized = doi.replace("/", "_").replace(" ", "_")
    candidate = pdf_dir / f"{normalized}.pdf"
    if candidate.exists():
        logger.info("Found PDF for %s at %s", doi, candidate)
        return candidate
    logger.info("PDF for %s not found under %s", doi, pdf_dir)
    return None
