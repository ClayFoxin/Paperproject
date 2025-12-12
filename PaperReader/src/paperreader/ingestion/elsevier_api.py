"""Elsevier API interactions for downloading article XML."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


class ElsevierClient:
    """Lightweight Elsevier API client for fetching XML by DOI."""

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, timeout: int = 30):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout

    def _build_url(self, doi: str) -> str:
        doi_encoded = quote(doi)
        return (
            "https://api.elsevier.com/content/article/doi/"
            f"{doi_encoded}?apiKey={self.api_key}&httpAccept=application/xml"
        )

    def download_xml(self, doi: str, destination: Path) -> Optional[Path]:
        """Download article XML by DOI with retry logic."""
        destination.parent.mkdir(parents=True, exist_ok=True)

        if not self.api_key:
            logger.error("Elsevier API key missing. Cannot download %s", doi)
            return None

        url = self._build_url(doi)
        headers = {"Accept": "application/xml"}

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
            except Exception as exc:  # pragma: no cover - network exceptions
                logger.warning("Attempt %s errored for %s: %s", attempt, doi, exc)
                if attempt < self.max_retries:
                    time.sleep(3)
                continue

            if response.status_code == 200:
                destination.write_bytes(response.content)
                logger.info("Downloaded XML for %s", doi)
                return destination

            if response.status_code == 404:
                logger.warning("Article not found or unauthorized for %s (404)", doi)
                return None

            logger.error("Download failed for %s | status %s", doi, response.status_code)
            if attempt < self.max_retries:
                time.sleep(3)

        return None
