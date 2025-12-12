"""Main orchestrator for the end-to-end pipeline."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from paperreader.cleaning.strip_metadata import strip_metadata
from paperreader.config import Settings
from paperreader.ingestion.elsevier_api import ElsevierClient
from paperreader.ingestion.uploader import resolve_pdf
from paperreader.ingestion.uniparser_adapter import parse_document
from paperreader.io.doi_loader import load_doi_list
from paperreader.io.json_store import save_json
from paperreader.io.xlsx_writer import write_records_to_xlsx
from paperreader.llm.client import LLMClient
from paperreader.llm.data_extract import DEFAULT_FIELDS, extract_data
from paperreader.llm.info_extract import extract_info
from paperreader.utils.log import get_logger

logger = get_logger(__name__)


def _build_output_path(base: Path, doi: str, suffix: str) -> Path:
    safe = doi.replace("/", "_")
    return base / f"{safe}{suffix}"


def run_pipeline(settings: Settings) -> None:
    dois = load_doi_list(settings.input_doi)
    if not dois:
        logger.warning("No DOIs to process; exiting")
        return

    llm_client = LLMClient(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
    )
    elsevier = ElsevierClient(api_key=settings.elsevier_api_key)

    structured_rows: List[dict] = []

    for doi in dois:
        logger.info("Processing DOI %s", doi)
        xml_path = _build_output_path(settings.output_parsed, doi, ".xml")
        json_path = _build_output_path(settings.output_parsed, doi, ".json")
        cleaned_path = _build_output_path(settings.output_cleaned, doi, ".json")
        info_path = _build_output_path(settings.output_info, doi, ".json")

        downloaded_xml = elsevier.download_xml(doi, xml_path)
        pdf_path = resolve_pdf(doi, settings.input_pdfs)
        source = pdf_path or (downloaded_xml if downloaded_xml else xml_path)

        parsed_doc = parse_document(source, json_path, doi=doi)
        cleaned_doc = strip_metadata(parsed_doc)
        save_json(parsed_doc, json_path)
        save_json(cleaned_doc, cleaned_path)

        info = extract_info(llm_client, cleaned_doc)
        save_json(info.to_dict(), info_path)

        records = extract_data(llm_client, cleaned_doc, fields=DEFAULT_FIELDS)
        for record in records:
            row = record.to_dict()
            row.update({"doi": doi})
            structured_rows.append(row)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    xlsx_path = settings.output_xlsx / f"extracted_{timestamp}.xlsx"
    write_records_to_xlsx(structured_rows, xlsx_path)
    logger.info("Pipeline complete. Results written to %s", xlsx_path)
