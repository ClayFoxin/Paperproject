"""Configuration loading utilities for PaperReader."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    base_dir: Path
    data_dir: Path
    input_doi: Path
    input_pdfs: Path
    output_parsed: Path
    output_cleaned: Path
    output_info: Path
    output_xlsx: Path
    openai_api_key: Optional[str]
    openai_base_url: Optional[str]
    openai_model: str
    elsevier_api_key: Optional[str]
    uniparser_cli_path: Optional[str]
    uniparser_host: Optional[str]
    uniparser_token: Optional[str]


def load_settings(env_path: Optional[Path] = None) -> Settings:
    """Load settings from environment variables and resolve filesystem paths."""
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    base_dir = Path(__file__).resolve().parents[2]
    data_dir = base_dir / "data"
    input_dir = data_dir / "input"
    output_dir = data_dir / "output"

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_base_url = os.getenv("OPENAI_BASE_URL")
    openai_model = os.getenv("OPENAI_MODEL") or (
        "deepseek-chat" if openai_base_url and "deepseek" in openai_base_url.lower() else "gpt-4o-mini"
    )

    settings = Settings(
        base_dir=base_dir,
        data_dir=data_dir,
        input_doi=input_dir / "doi.xlsx",
        input_pdfs=input_dir / "pdfs",
        output_parsed=output_dir / "parsed_json",
        output_cleaned=output_dir / "cleaned_json",
        output_info=output_dir / "info_json",
        output_xlsx=output_dir / "extracted_xlsx",
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_model=openai_model,
        elsevier_api_key=os.getenv("ELSEVIER_API_KEY"),
        uniparser_cli_path=os.getenv("UNIPARSER_CLI_PATH"),
        uniparser_host=os.getenv("UNIPARSER_HOST") or "http://101.126.82.63:40001",
        uniparser_token=os.getenv("UNIPARSER_TOKEN") or "article",
    )

    return settings
