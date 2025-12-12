"""Placeholder for Elsevier API interactions."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import requests

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


class ElsevierClient:
    """Lightweight Elsevier API client (placeholder)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def download_xml(self, doi: str, destination: Path) -> Optional[Path]:
        """Download article XML by DOI. Currently a stub that creates an empty file."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not self.api_key:
            logger.warning("Elsevier API key missing. Creating placeholder XML for %s", doi)
            destination.write_text("<!-- placeholder xml for %s -->" % doi, encoding="utf-8")
            return destination

        headers = {"X-ELS-APIKey": self.api_key}
        url = f"https://api.elsevier.com/content/article/doi/{doi}?view=FULL"
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            destination.write_bytes(response.content)
            logger.info("Downloaded XML for %s", doi)
            return destination

        logger.error("Failed to download XML for %s (status %s)", doi, response.status_code)
        return None
