"""Export structured data to XLSX."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def write_records_to_xlsx(records: Iterable[Mapping], path: Path) -> None:
    df = pd.DataFrame(list(records))
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)
    logger.info("Wrote %d rows to %s", len(df), path)
