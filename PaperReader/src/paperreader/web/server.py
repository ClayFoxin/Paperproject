"""FastAPI web UI for PaperReader pipeline."""
from __future__ import annotations

import threading
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from paperreader.config import Settings, load_settings
from paperreader.pipeline.run import run_pipeline
from paperreader.utils.log import get_logger

logger = get_logger(__name__)

app = FastAPI(title="PaperReader Web UI", version="0.1.0")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


class PipelineState:
    """In-memory pipeline status tracker."""

    def __init__(self) -> None:
        self.running: bool = False
        self.last_start: Optional[datetime] = None
        self.last_finish: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.last_output: Optional[Path] = None
        self.lock = threading.Lock()

    def start(self) -> bool:
        with self.lock:
            if self.running:
                return False
            self.running = True
            self.last_start = datetime.utcnow()
            self.last_error = None
            return True

    def finish(self, output_path: Optional[Path] = None, error: Optional[str] = None) -> None:
        with self.lock:
            self.running = False
            self.last_finish = datetime.utcnow()
            self.last_output = output_path
            self.last_error = error


state = PipelineState()


def ensure_directories(settings: Settings) -> None:
    for path in [
        settings.input_doi.parent,
        settings.input_pdfs,
        settings.output_parsed,
        settings.output_cleaned,
        settings.output_info,
        settings.output_xlsx,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def latest_output(xlsx_dir: Path) -> Optional[Path]:
    files = list(xlsx_dir.glob("*.xlsx"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def _run_pipeline_background(settings: Settings) -> None:
    logger.info("Pipeline background task started")
    try:
        run_pipeline(settings)
        state.finish(output_path=latest_output(settings.output_xlsx))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline failed: %s", exc)
        state.finish(error=str(exc))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    settings = load_settings()
    ensure_directories(settings)
    pdfs = sorted(settings.input_pdfs.glob("*.pdf"))
    parsed_files = sorted(settings.output_parsed.glob("*.json"))
    cleaned_files = sorted(settings.output_cleaned.glob("*.json"))
    info_files = sorted(settings.output_info.glob("*.json"))
    xlsx_files = sorted(settings.output_xlsx.glob("*.xlsx"))

    context: Dict[str, object] = {
        "request": request,
        "state": state,
        "settings": settings,
        "pdfs": pdfs,
        "parsed_files": parsed_files,
        "cleaned_files": cleaned_files,
        "info_files": info_files,
        "xlsx_files": xlsx_files,
    }
    return templates.TemplateResponse("index.html", context)


@app.post("/upload/doi")
async def upload_doi(file: UploadFile = File(...)) -> RedirectResponse:
    settings = load_settings()
    ensure_directories(settings)
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 格式的 DOI 文件")

    dest = settings.input_doi
    content = await file.read()
    dest.write_bytes(content)
    logger.info("Uploaded DOI list to %s", dest)
    return RedirectResponse(url="/", status_code=303)


@app.post("/upload/pdfs")
async def upload_pdfs(files: List[UploadFile] = File(...)) -> RedirectResponse:
    settings = load_settings()
    ensure_directories(settings)
    saved = 0
    for upload in files:
        if not upload.filename.lower().endswith(".pdf"):
            continue
        target = settings.input_pdfs / Path(upload.filename).name
        target.write_bytes(await upload.read())
        saved += 1
    if saved == 0:
        raise HTTPException(status_code=400, detail="没有有效的 PDF 被上传")
    logger.info("Saved %s PDFs to %s", saved, settings.input_pdfs)
    return RedirectResponse(url="/", status_code=303)


@app.post("/run")
async def run_endpoint(
    background_tasks: BackgroundTasks,
    openai_api_key: Optional[str] = Form(None),
    openai_base_url: Optional[str] = Form(None),
    elsevier_api_key: Optional[str] = Form(None),
) -> RedirectResponse:
    if not state.start():
        raise HTTPException(status_code=409, detail="流水线正在运行中")

    settings = load_settings()
    ensure_directories(settings)

    if openai_api_key:
        settings = replace(settings, openai_api_key=openai_api_key.strip())
    if openai_base_url:
        settings = replace(settings, openai_base_url=openai_base_url.strip())
    if elsevier_api_key:
        settings = replace(settings, elsevier_api_key=elsevier_api_key.strip())

    background_tasks.add_task(_run_pipeline_background, settings)
    return RedirectResponse(url="/", status_code=303)


@app.get("/download")
async def download(path: str) -> FileResponse:
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(file_path)
