#!/opt/claw-ed/venv/bin/python
from __future__ import annotations

import json
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP


ENV_PATH = Path("/opt/hermes-ragflow/ragflow.env")


def _load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env()
mcp = FastMCP("teacher-ragflow")


def _base_url() -> str:
    return os.getenv("RAGFLOW_BASE_URL", "http://127.0.0.1:19380").rstrip("/")


def _api_key() -> str:
    key = os.getenv("RAGFLOW_API_KEY", "").strip()
    if not key:
        raise RuntimeError("RAGFLOW_API_KEY is missing")
    return key


def _archive_url() -> str:
    return os.getenv("TEACHER_FILE_ARCHIVE_URL", "http://127.0.0.1:18765/store").strip()


def _teacher_api_base() -> str:
    return os.getenv("TEACHER_RESOURCE_API_URL", "http://127.0.0.1:15128/api").rstrip("/")


def _paper_worker_url() -> str:
    return os.getenv("PAPER_ASSET_WORKER_URL", "http://127.0.0.1:18766").rstrip("/")


def _paper_worker_token() -> str:
    return os.getenv("PAPER_ASSET_WORKER_TOKEN", "").strip()


def _paper_output_dir() -> Path:
    return Path(os.getenv("PAPER_ASSET_OUTPUT_DIR", "/opt/hermes-ragflow/outputs/paper-assets"))


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_api_key()}"}


def _request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    timeout = kwargs.pop("timeout", 120)
    response = requests.request(method, url, headers=_headers(), timeout=timeout, **kwargs)
    try:
        data = response.json()
    except Exception:
        data = {"status_code": response.status_code, "text": response.text[:2000]}
    if response.status_code >= 400:
        raise RuntimeError(f"RAGFlow HTTP {response.status_code}: {data}")
    if isinstance(data, dict) and data.get("code") not in (0, None):
        raise RuntimeError(f"RAGFlow API error: {data}")
    return data


def _dataset_id(dataset_name: str = "", dataset_id: str = "") -> str:
    if dataset_id:
        return dataset_id
    if not dataset_name:
        raise ValueError("dataset_name or dataset_id is required")
    data = _request("GET", "/api/v1/datasets", params={"page": 1, "page_size": 30, "name": dataset_name})
    rows = data.get("data") or []
    for row in rows:
        if row.get("name") == dataset_name:
            return row["id"]
    raise ValueError(f"dataset not found: {dataset_name}")


def _dataset_label(dataset_name: str = "", dataset_id: str = "") -> str:
    if dataset_name:
        return dataset_name
    if not dataset_id:
        return "默认资料库"
    try:
        data = _request("GET", "/api/v1/datasets", params={"page": 1, "page_size": 100})
        for row in data.get("data") or []:
            if row.get("id") == dataset_id and row.get("name"):
                return row["name"]
    except Exception:
        pass
    return dataset_id


def _archive_teacher_file(path: Path, dataset_name: str = "", dataset_id: str = "") -> dict[str, Any]:
    url = _archive_url()
    if not url:
        return {"ok": False, "skipped": True, "reason": "TEACHER_FILE_ARCHIVE_URL is empty"}

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as fh:
        response = requests.post(
            url,
            data={"dataset": _dataset_label(dataset_name, dataset_id)},
            files={"file": (path.name, fh, mime)},
            timeout=600,
        )
    try:
        data = response.json()
    except Exception:
        data = {"text": response.text[:2000]}
    if response.status_code >= 400:
        raise RuntimeError(f"teacher file archive HTTP {response.status_code}: {data}")
    return data


def _compact(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)[:12000]


def _teacher_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{_teacher_api_base()}{path}"
    timeout = kwargs.pop("timeout", 120)
    response = requests.request(method, url, timeout=timeout, **kwargs)
    try:
        data = response.json()
    except Exception:
        data = {"status_code": response.status_code, "text": response.text[:2000]}
    if response.status_code >= 400:
        raise RuntimeError(f"TeacherResource HTTP {response.status_code}: {data}")
    if isinstance(data, dict) and data.get("success") is False:
        raise RuntimeError(f"TeacherResource API error: {data}")
    return data


def _paper_headers() -> dict[str, str]:
    token = _paper_worker_token()
    return {"x-worker-token": token} if token else {}


def _paper_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{_paper_worker_url()}{path}"
    timeout = kwargs.pop("timeout", 1800)
    headers = kwargs.pop("headers", {})
    merged_headers = {**_paper_headers(), **headers}
    response = requests.request(method, url, headers=merged_headers, timeout=timeout, **kwargs)
    try:
        data = response.json()
    except Exception:
        data = {"status_code": response.status_code, "text": response.text[:2000]}
    if response.status_code >= 400:
        raise RuntimeError(f"Paper asset worker HTTP {response.status_code}: {data}")
    return data


def _download_paper_asset(job_id: str, filename: str, out_dir: Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    url = f"{_paper_worker_url()}/jobs/{job_id}/{filename}"
    response = requests.get(url, headers=_paper_headers(), timeout=600)
    if response.status_code >= 400:
        try:
            data = response.json()
        except Exception:
            data = response.text[:2000]
        raise RuntimeError(f"Paper asset download failed {filename}: {response.status_code} {data}")
    path = out_dir / filename
    path.write_bytes(response.content)
    return str(path)


@mcp.tool(description="检查 RAGFlow 是否在线，并列出当前资料库/知识库。")
def ragflow_status() -> str:
    health = requests.get(f"{_base_url()}/api/v1/system/healthz", timeout=20).json()
    datasets = _request("GET", "/api/v1/datasets", params={"page": 1, "page_size": 20})
    return _compact({"base_url": _base_url(), "health": health, "datasets": datasets})


@mcp.tool(description="创建 RAGFlow 资料库/知识库。用户说创建库、创建资料库、创建知识库、创建题库、创建试卷库时优先用这个工具。")
def ragflow_create_dataset(
    name: str,
    description: str = "",
    permission: str = "me",
    chunk_method: str = "naive",
) -> str:
    payload = {
        "name": name,
        "description": description,
        "permission": permission,
        "chunk_method": chunk_method,
    }
    data = _request("POST", "/api/v1/datasets", json=payload)
    return _compact(data)


@mcp.tool(description="中文快捷工具：创建一个老师资料库/知识库/题库/试卷库。适合飞书里说“帮我创建一个某某库”。")
def ragflow_create_teacher_library(
    name: str,
    description: str = "",
    library_type: str = "资料库",
) -> str:
    if not description:
        description = f"{name}，用于存放老师上传的教材、讲义、试卷、答案、解析、错题和课堂资料，支持后续检索、问答、生成教案、出题和制作材料。"
    return ragflow_create_dataset(
        name=name,
        description=description,
        permission="me",
        chunk_method="naive",
    )


@mcp.tool(description="列出 RAGFlow 资料库/知识库，可按名称过滤。")
def ragflow_list_datasets(name: str = "", page_size: int = 30) -> str:
    params: dict[str, Any] = {"page": 1, "page_size": page_size}
    if name:
        params["name"] = name
    return _compact(_request("GET", "/api/v1/datasets", params=params))


@mcp.tool(description="把飞书上传后保存在服务器的本地文件入库到 RAGFlow，并同步一份原文件到 D:\\HermesRAG\\teacher-files\\资料库名。")
def ragflow_ingest_file(
    source_path: str,
    dataset_name: str = "",
    dataset_id: str = "",
    parse: bool = True,
) -> str:
    path = Path(source_path).expanduser()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"source file not found: {source_path}")

    ds_id = _dataset_id(dataset_name=dataset_name, dataset_id=dataset_id)
    result: dict[str, Any] = {"dataset_id": ds_id}
    try:
        result["local_archive"] = _archive_teacher_file(path, dataset_name=dataset_name, dataset_id=ds_id)
    except Exception as exc:
        result["local_archive"] = {"ok": False, "error": str(exc)}

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as fh:
        files = [("file", (path.name, fh, mime))]
        uploaded = _request("POST", f"/api/v1/datasets/{ds_id}/documents", files=files, timeout=600)

    result["uploaded"] = uploaded
    doc_ids: list[str] = []
    for item in uploaded.get("data") or []:
        if isinstance(item, dict) and item.get("id"):
            doc_ids.append(item["id"])

    if parse and doc_ids:
        result["parse"] = _request("POST", f"/api/v1/datasets/{ds_id}/chunks", json={"document_ids": doc_ids}, timeout=300)
    return _compact(result)


@mcp.tool(description="从指定 RAGFlow 资料库/知识库检索与老师问题最相关的内容片段。")
def ragflow_retrieve(
    question: str,
    dataset_name: str = "",
    dataset_id: str = "",
    top_k: int = 8,
    similarity_threshold: float = 0.2,
    keyword: bool = False,
) -> str:
    ds_id = _dataset_id(dataset_name=dataset_name, dataset_id=dataset_id)
    payload = {
        "question": question,
        "dataset_ids": [ds_id],
        "page": 1,
        "page_size": max(1, min(top_k, 30)),
        "top_k": max(8, top_k),
        "similarity_threshold": similarity_threshold,
        "keyword": keyword,
    }
    data = _request("POST", "/api/v1/retrieval", json=payload, timeout=120)
    return _compact(data)


@mcp.tool(description="检查 teacher-resource 后台是否在线，并返回它连接 RAGFlow 的状态。")
def teacher_resource_status() -> str:
    health = _teacher_request("GET", "/health")
    ragflow = _teacher_request("GET", "/ragflow/status")
    return _compact({"teacher_resource": health, "ragflow_bridge": ragflow})


@mcp.tool(description="从 teacher-resource 后台查询教学资源，可按关键词、解析状态、可调用状态过滤。")
def teacher_resource_list_resources(
    organization_id: int = 1,
    keyword: str = "",
    parse_status: str = "",
    callable_status: str = "",
    page_size: int = 20,
) -> str:
    params: dict[str, Any] = {
        "organizationId": organization_id,
        "pageIndex": 1,
        "pageSize": max(1, min(page_size, 100)),
    }
    if keyword:
        params["keyword"] = keyword
    if parse_status:
        params["parseStatus"] = parse_status
    if callable_status:
        params["callableStatus"] = callable_status
    return _compact(_teacher_request("GET", "/resources", params=params))


@mcp.tool(description="让 teacher-resource 后台把某个资源文件入库到 RAGFlow，并更新资源解析状态。")
def teacher_resource_ingest_file(
    resource_id: int,
    file_id: int,
    dataset_name: str = "",
    dataset_id: str = "",
    parse: bool = True,
    operator_id: int = 1,
) -> str:
    payload = {
        "datasetName": dataset_name,
        "datasetId": dataset_id,
        "parse": parse,
        "operatorId": operator_id,
    }
    return _compact(_teacher_request(
        "POST",
        f"/ragflow/resources/{resource_id}/files/{file_id}/ingest",
        json=payload,
        timeout=900,
    ))


@mcp.tool(description="同步某个 teacher-resource 资源在 RAGFlow 里的解析状态、切片数和可调用状态。")
def teacher_resource_sync_resource(resource_id: int) -> str:
    return _compact(_teacher_request("POST", f"/ragflow/resources/{resource_id}/sync", timeout=120))


@mcp.tool(description="查看某个 teacher-resource 资源对应的 RAGFlow 切片结果。")
def teacher_resource_chunks(resource_id: int) -> str:
    return _compact(_teacher_request("GET", f"/ragflow/resources/{resource_id}/chunks", timeout=120))


@mcp.tool(description="把 teacher-resource 的上下文包整体入库到 RAGFlow，适合把一组教学资料变成一个资料库。")
def teacher_resource_ingest_context_pack(
    context_pack_id: int,
    dataset_name: str = "",
    dataset_id: str = "",
    parse: bool = True,
    operator_id: int = 1,
) -> str:
    payload = {
        "datasetName": dataset_name,
        "datasetId": dataset_id,
        "parse": parse,
        "operatorId": operator_id,
    }
    return _compact(_teacher_request(
        "POST",
        f"/ragflow/context-packs/{context_pack_id}/ingest",
        json=payload,
        timeout=1800,
    ))


@mcp.tool(description="旧试卷清版并生成可交付教学资产包：去手写/批改痕迹，识别题型、知识点、答案解析，判断难度与适配度，生成变式题，自动排版输出 DOCX、PDF、题库 JSON 和 ZIP；可选入库到 RAGFlow。")
def teacher_paper_asset_package(
    source_path: str,
    title: str = "",
    subject: str = "",
    grade: str = "",
    dataset_name: str = "",
    dataset_id: str = "",
    ingest_to_ragflow: bool = False,
    max_pages: int = 12,
) -> str:
    path = Path(source_path).expanduser()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"source file not found: {source_path}")

    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    with path.open("rb") as fh:
        response = requests.post(
            f"{_paper_worker_url()}/make",
            headers=_paper_headers(),
            data={
                "title": title,
                "subject": subject,
                "grade": grade,
                "max_pages": str(max(1, min(max_pages, 40))),
            },
            files={"file": (path.name, fh, mime)},
            timeout=1800,
        )
    try:
        worker_data = response.json()
    except Exception:
        worker_data = {"status_code": response.status_code, "text": response.text[:2000]}
    if response.status_code >= 400:
        raise RuntimeError(f"Paper asset worker HTTP {response.status_code}: {worker_data}")

    job_id = worker_data.get("job_id")
    if not job_id:
        raise RuntimeError(f"Paper asset worker did not return job_id: {worker_data}")

    out_dir = _paper_output_dir() / job_id
    downloaded: dict[str, str] = {}
    for filename, key in [
        ("clean_paper.docx", "docx"),
        ("clean_paper.pdf", "pdf"),
        ("question_bank.json", "question_bank_json"),
        ("analysis.md", "analysis_md"),
        ("asset_package.zip", "zip"),
    ]:
        downloaded[key] = _download_paper_asset(job_id, filename, out_dir)

    result: dict[str, Any] = {
        "ok": True,
        "job_id": job_id,
        "question_count": worker_data.get("question_count"),
        "server_output_dir": str(out_dir),
        "files": downloaded,
        "worker": {
            "url": _paper_worker_url(),
            "out_dir": worker_data.get("out_dir"),
        },
    }

    if ingest_to_ragflow:
        if not dataset_name and not dataset_id:
            result["ragflow_ingest"] = {
                "ok": False,
                "skipped": True,
                "reason": "ingest_to_ragflow=true but dataset_name/dataset_id is empty",
            }
        else:
            result["ragflow_ingest"] = ragflow_ingest_file(
                source_path=downloaded["pdf"],
                dataset_name=dataset_name,
                dataset_id=dataset_id,
                parse=True,
            )

    return _compact(result)


def _self_test() -> int:
    print(ragflow_status())
    try:
        print(teacher_resource_status())
    except Exception as exc:
        print(f"teacher-resource unavailable: {exc}")
    try:
        print(_compact(_paper_request("GET", "/health", timeout=20)))
    except Exception as exc:
        print(f"paper asset worker unavailable: {exc}")
    return 0


if __name__ == "__main__":
    import sys

    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    mcp.run("stdio")
