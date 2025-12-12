"""Load DOI list from Excel files."""
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def load_doi_list(path: Path) -> List[str]:
    """Load DOIs from an Excel file with a column named `doi` (case-insensitive)."""
    if not path.exists():
        logger.warning("DOI file not found at %s", path)
        return []

    df = pd.read_excel(path)
    normalized_columns = {col.lower(): col for col in df.columns}
    doi_col = normalized_columns.get("doi")
    if not doi_col:
        logger.warning("No 'doi' column found in %s", path)
        return []

    doi_series = df[doi_col].dropna().astype(str).str.strip()
    dois = [doi for doi in doi_series if doi]
    logger.info("Loaded %d DOIs from %s", len(dois), path)
    return dois
