from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote


DEFAULT_ROOT = Path(r"D:\HermesRAG\teacher-files")
INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_name(value: str, fallback: str) -> str:
    value = unquote(value or "").strip().strip(".")
    value = INVALID_CHARS.sub("_", value)
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        value = fallback
    if value.upper() in RESERVED_NAMES:
        value = f"{value}_"
    return value[:120]


def unique_path(directory: Path, filename: str) -> Path:
    target = directory / filename
    if not target.exists():
        return target

    stem = target.stem or "file"
    suffix = target.suffix
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for index in range(1, 1000):
        candidate = directory / f"{stem}_{stamp}_{index}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not allocate a unique name for {filename}")


def parse_multipart(headers: dict[str, str], body: bytes) -> tuple[str, str, bytes]:
    content_type = headers.get("content-type", "")
    if "multipart/form-data" not in content_type.lower():
        raise ValueError("Expected multipart/form-data")

    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    )

    dataset = ""
    filename = ""
    payload = b""

    for part in message.iter_parts():
        disposition = part.get("Content-Disposition", "")
        if "form-data" not in disposition:
            continue
        name = part.get_param("name", header="content-disposition") or ""
        if name == "dataset":
            raw = part.get_payload(decode=True) or b""
            dataset = raw.decode(part.get_content_charset() or "utf-8", errors="replace")
        elif name == "file":
            filename = part.get_param("filename", header="content-disposition") or "uploaded-file"
            payload = part.get_payload(decode=True) or b""

    if not payload:
        raise ValueError("Missing file payload")
    return dataset, filename, payload


class TeacherFileReceiver(BaseHTTPRequestHandler):
    server_version = "TeacherFileReceiver/1.0"

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/healthz":
            self.send_json({"ok": True, "root": str(self.server.root_dir)})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/store":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                raise ValueError("Empty request body")
            if length > self.server.max_bytes:
                raise ValueError(f"File is too large: {length} bytes")

            body = self.rfile.read(length)
            headers = {key.lower(): value for key, value in self.headers.items()}
            dataset, filename, payload = parse_multipart(headers, body)

            dataset_dir = self.server.root_dir / safe_name(dataset, "默认资料库")
            dataset_dir.mkdir(parents=True, exist_ok=True)
            target = unique_path(dataset_dir, safe_name(filename, "uploaded-file"))
            tmp = target.with_suffix(target.suffix + ".tmp")
            tmp.write_bytes(payload)
            os.replace(tmp, target)

            self.send_json(
                {
                    "ok": True,
                    "dataset": dataset_dir.name,
                    "filename": target.name,
                    "path": str(target),
                    "bytes": len(payload),
                }
            )
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stdout.write(f"{datetime.now().isoformat(timespec='seconds')} {self.address_string()} {fmt % args}\n")
        sys.stdout.flush()

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


class ReceiverServer(ThreadingHTTPServer):
    root_dir: Path
    max_bytes: int


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18765)
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--max-mb", type=int, default=1024)
    args = parser.parse_args()

    server = ReceiverServer((args.host, args.port), TeacherFileReceiver)
    server.root_dir = Path(args.root)
    server.root_dir.mkdir(parents=True, exist_ok=True)
    server.max_bytes = args.max_mb * 1024 * 1024

    print(f"Teacher file receiver listening on http://{args.host}:{args.port}")
    print(f"Saving files under {server.root_dir}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
