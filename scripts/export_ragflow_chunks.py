from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import requests


ROOT = Path(r"D:\HermesRAG")
API_KEY_FILE = ROOT / "ragflow-api-key.txt"
OUTPUT_ROOT = ROOT / "teacher-files"
DEFAULT_BASE_URL = "http://127.0.0.1:9380"
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def safe_name(value: str, fallback: str = "untitled") -> str:
    value = INVALID_CHARS.sub("_", value or "").strip().strip(".")
    value = re.sub(r"\s+", " ", value)
    return (value or fallback)[:160]


def request_json(method: str, url: str, token: str, **kwargs: Any) -> dict[str, Any]:
    response = requests.request(
        method,
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
        **kwargs,
    )
    response.encoding = "utf-8"
    response.raise_for_status()
    data = response.json()
    if data.get("code") not in (0, None):
        raise RuntimeError(f"RAGFlow API error: {data}")
    return data


def find_dataset(base_url: str, token: str, name: str) -> dict[str, Any]:
    data = request_json(
        "GET",
        f"{base_url}/api/v1/datasets",
        token,
        params={"page": 1, "page_size": 100},
    )
    for dataset in data.get("data") or []:
        if dataset.get("name") == name:
            return dataset
    raise ValueError(f"Dataset not found: {name}")


def list_documents(base_url: str, token: str, dataset_id: str) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    page = 1
    while True:
        data = request_json(
            "GET",
            f"{base_url}/api/v1/datasets/{dataset_id}/documents",
            token,
            params={"page": page, "page_size": 100},
        )
        payload = data.get("data") or {}
        rows = payload.get("docs") or []
        docs.extend(rows)
        if len(rows) < 100:
            return docs
        page += 1


def list_chunks(base_url: str, token: str, dataset_id: str, document_id: str) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    page = 1
    while True:
        data = request_json(
            "GET",
            f"{base_url}/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks",
            token,
            params={"page": page, "page_size": 100},
        )
        payload = data.get("data") or {}
        rows = payload.get("chunks") or []
        chunks.extend(rows)
        total = int(payload.get("total") or len(chunks))
        if len(chunks) >= total or len(rows) < 100:
            return chunks
        page += 1


def write_exports(dataset_name: str, document: dict[str, Any], chunks: list[dict[str, Any]]) -> tuple[Path, Path]:
    out_dir = OUTPUT_ROOT / safe_name(dataset_name) / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)
    doc_name = document.get("name") or document.get("location") or document.get("id") or "document"
    stem = safe_name(Path(doc_name).stem)

    json_path = out_dir / f"{stem}.chunks.json"
    md_path = out_dir / f"{stem}.chunks.md"

    json_path.write_text(
        json.dumps({"document": document, "chunks": chunks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# {doc_name}",
        "",
        f"- dataset: {dataset_name}",
        f"- document_id: {document.get('id', '')}",
        f"- chunk_count: {len(chunks)}",
        f"- source_file: {document.get('location', '')}",
        "",
    ]
    for index, chunk in enumerate(chunks, start=1):
        content = (chunk.get("content") or chunk.get("text") or "").strip()
        chunk_id = chunk.get("id", "")
        available = chunk.get("available", "")
        important = chunk.get("important_kwd") or chunk.get("important_keywords") or []
        lines.extend(
            [
                f"## Chunk {index:03d}",
                "",
                f"- id: `{chunk_id}`",
                f"- available: `{available}`",
                f"- keywords: {', '.join(important) if isinstance(important, list) else important}",
                "",
                content,
                "",
            ]
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--document", default="", help="Optional exact or partial document name.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    token = API_KEY_FILE.read_text(encoding="utf-8").strip()
    dataset = find_dataset(args.base_url.rstrip("/"), token, args.dataset)
    documents = list_documents(args.base_url.rstrip("/"), token, dataset["id"])
    if args.document:
        needle = args.document
        documents = [
            doc
            for doc in documents
            if needle in (doc.get("name") or "") or needle in (doc.get("location") or "")
        ]
    if not documents:
        raise ValueError(f"No documents found in dataset: {args.dataset}")

    for document in documents:
        chunks = list_chunks(args.base_url.rstrip("/"), token, dataset["id"], document["id"])
        md_path, json_path = write_exports(args.dataset, document, chunks)
        print(f"Exported {len(chunks)} chunks")
        print(md_path)
        print(json_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
