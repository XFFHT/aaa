from __future__ import annotations

import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pipeline import DEFAULT_OUTPUT_DIR, ROOT, load_env, make_asset_package


load_env()

app = FastAPI(title="Old Paper Asset Worker", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def output_root() -> Path:
    return Path(os.getenv("OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR))).expanduser().resolve()


def expected_token() -> str:
    return os.getenv("WORKER_TOKEN", "").strip()


def verify_token(x_worker_token: str | None) -> None:
    token = expected_token()
    if token and x_worker_token != token:
        raise HTTPException(status_code=401, detail="invalid worker token")


def safe_name(name: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch in ".-_()[] " else "_" for ch in name).strip()
    return clean or "upload.bin"


def file_url(request: Request, job_id: str, filename: str) -> str:
    return str(request.url_for("download_file", job_id=job_id, filename=filename))


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "root": str(ROOT),
        "output_dir": str(output_root()),
        "model": os.getenv("OPENAI_MODEL", "gpt-5.5"),
        "has_api_key": bool(os.getenv("OPENAI_API_KEY", "").strip()),
    }


@app.post("/make")
async def make(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(""),
    subject: str = Form(""),
    grade: str = Form(""),
    max_pages: int = Form(12),
    x_worker_token: str | None = Header(None),
) -> dict[str, Any]:
    verify_token(x_worker_token)
    suffix = Path(file.filename or "upload.bin").suffix
    temp_dir = Path(tempfile.mkdtemp(prefix="paper_asset_"))
    temp_path = temp_dir / safe_name(file.filename or ("upload" + suffix))
    try:
        with temp_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
        result = await run_in_threadpool(
            make_asset_package,
            temp_path,
            title,
            subject,
            grade,
            max(1, min(max_pages, 40)),
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    job_id = result["job_id"]
    downloads = {
        "docx": file_url(request, job_id, "clean_paper.docx"),
        "pdf": file_url(request, job_id, "clean_paper.pdf"),
        "question_bank_json": file_url(request, job_id, "question_bank.json"),
        "analysis_md": file_url(request, job_id, "analysis.md"),
        "zip": file_url(request, job_id, "asset_package.zip"),
    }
    result["downloads"] = downloads
    return result


@app.get("/jobs/{job_id}/{filename}", name="download_file")
def download_file(job_id: str, filename: str, x_worker_token: str | None = Header(None)) -> FileResponse:
    verify_token(x_worker_token)
    root = output_root()
    path = (root / job_id / filename).resolve()
    if root not in path.parents:
        raise HTTPException(status_code=400, detail="invalid path")
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return FileResponse(str(path), media_type=media_type, filename=path.name)
