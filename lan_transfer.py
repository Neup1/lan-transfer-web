#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import http.client
import json
import mimetypes
import os
import secrets
import socket
import string
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from lan_transfer_frontend import WEB_UI_HTML
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import parse_qs, quote, urlsplit


IO_CHUNK = 4 * 1024 * 1024
DEFAULT_PORT = 9000
DEFAULT_TIMEOUT = 30.0
DEFAULT_TOKEN_TTL = 2 * 3600
DEFAULT_CHALLENGE_TTL = 60
JSON_LIMIT = 1024 * 1024
ASSET_ROOT = Path(__file__).resolve().parent / "assets"

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def now_ts() -> int:
    return int(time.time())


def detect_lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
    except OSError:
        pass
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except OSError:
        pass
    return "127.0.0.1"


def detect_local_ips() -> set[str]:
    ips: set[str] = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}
    try:
        for family, _, _, _, sockaddr in socket.getaddrinfo(socket.gethostname(), None):
            if family in (socket.AF_INET, socket.AF_INET6):
                ip = sockaddr[0]
                if ip:
                    ips.add(ip.split("%")[0])
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip:
                ips.add(ip)
    except OSError:
        pass
    ips.add(detect_lan_ip())
    return ips


def find_listening_pids(port: int) -> list[int]:
    if os.name != "nt":
        return []
    try:
        proc = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if proc.returncode != 0:
        return []
    pids: set[int] = set()
    suffix = f":{port}"
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line or "LISTENING" not in line:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local_addr = parts[1]
        state = parts[3]
        pid_str = parts[4]
        if state != "LISTENING":
            continue
        if not local_addr.endswith(suffix):
            continue
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        if pid != os.getpid():
            pids.add(pid)
    return sorted(pids)


def kill_processes(pids: list[int]) -> list[int]:
    if os.name != "nt":
        return []
    killed: list[int] = []
    for pid in pids:
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/F"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            killed.append(pid)
    return killed


def pick_directory_dialog(initial_dir: Path) -> Optional[Path]:
    """Open a native folder picker on server machine and return selected directory."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:  # pragma: no cover - depends on runtime GUI availability
        raise RuntimeError(f"Folder picker is unavailable: {exc}") from exc

    root: Optional["tk.Tk"] = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(
            parent=root,
            initialdir=str(initial_dir),
            mustexist=False,
            title="Select upload root directory",
        )
    except Exception as exc:  # pragma: no cover - depends on runtime GUI availability
        raise RuntimeError(f"Unable to open folder picker: {exc}") from exc
    finally:
        if root is not None:
            try:
                root.destroy()
            except Exception:
                pass

    if not selected:
        return None
    return Path(selected).expanduser().resolve()


def format_bytes(num_bytes: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} TiB"


def normalize_remote_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("/").strip()


def quote_remote_path(path: str) -> str:
    return quote(normalize_remote_path(path), safe="/")


def resolve_safe_path(root: Path, remote_path: str, *, allow_root: bool) -> Path:
    normalized = normalize_remote_path(remote_path)
    if normalized in ("", "."):
        if allow_root:
            return root
        raise ValueError("path cannot be empty")
    if "\x00" in normalized:
        raise ValueError("path contains invalid null byte")
    candidate = (root / normalized).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes shared root") from exc
    return candidate


@dataclass
class ServerState:
    # 服务端运行时认证状态（供所有请求处理器共享）。
    shared_root: Path
    password_key: bytes
    passphrase: str
    token_ttl: int = DEFAULT_TOKEN_TTL
    challenge_ttl: int = DEFAULT_CHALLENGE_TTL
    token_secret: bytes = field(default_factory=lambda: secrets.token_bytes(32))
    local_ips: set[str] = field(default_factory=detect_local_ips)
    challenges: Dict[str, float] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def get_shared_root(self) -> Path:
        with self.lock:
            return self.shared_root

    def set_shared_root(self, new_root: Path) -> Path:
        with self.lock:
            previous = self.shared_root
            self.shared_root = new_root
        return previous

    def _cleanup_challenges_locked(self) -> None:
        current = time.time()
        expired = [nonce for nonce, exp in self.challenges.items() if exp <= current]
        for nonce in expired:
            self.challenges.pop(nonce, None)

    def issue_challenge(self) -> tuple[str, int]:
        nonce = secrets.token_urlsafe(24)
        expires_at = time.time() + self.challenge_ttl
        with self.lock:
            self._cleanup_challenges_locked()
            self.challenges[nonce] = expires_at
        return nonce, self.challenge_ttl

    def verify_proof(self, nonce: str, proof: str) -> bool:
        with self.lock:
            self._cleanup_challenges_locked()
            expires_at = self.challenges.pop(nonce, None)
        if expires_at is None:
            return False
        expected = hmac.new(
            self.password_key,
            nonce.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, proof)

    def verify_password(self, password: str) -> bool:
        if not isinstance(password, str):
            return False
        return hmac.compare_digest(self.password_key, password.encode("utf-8"))

    def issue_token(self) -> str:
        payload = {
            "v": 1,
            "iat": now_ts(),
            "exp": now_ts() + self.token_ttl,
            "rnd": secrets.token_hex(4),
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
        sig = hmac.new(self.token_secret, payload_bytes, hashlib.sha256).digest()
        return f"{b64url_encode(payload_bytes)}.{b64url_encode(sig)}"

    def verify_token(self, token: str) -> bool:
        try:
            payload_enc, sig_enc = token.split(".", 1)
            payload_bytes = b64url_decode(payload_enc)
            sig = b64url_decode(sig_enc)
        except (ValueError, TypeError, base64.binascii.Error):
            return False
        expected_sig = hmac.new(self.token_secret, payload_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected_sig):
            return False
        try:
            payload = json.loads(payload_bytes)
            exp = int(payload.get("exp", 0))
        except (ValueError, TypeError):
            return False
        return now_ts() <= exp


def make_handler(state: ServerState):
    # 提供 HTTP API 与 Web 页面入口。
    class TransferHandler(BaseHTTPRequestHandler):
        server_version = "LANTransfer/1.0"
        protocol_version = "HTTP/1.1"

        def _send_json(self, status: int, data: dict) -> None:
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)

        def _send_html(self, status: int, html: str) -> None:
            payload = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)

        def _send_error(self, status: int, message: str) -> None:
            self._send_json(status, {"error": message})

        def _send_bytes(self, status: int, payload: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)

        def _read_json(self) -> Optional[dict]:
            content_length = self.headers.get("Content-Length")
            if content_length is None:
                self._send_error(411, "Content-Length is required")
                return None
            try:
                length = int(content_length)
            except ValueError:
                self._send_error(400, "Invalid Content-Length")
                return None
            if length < 0 or length > JSON_LIMIT:
                self._send_error(413, "Invalid JSON body length")
                return None
            body = self.rfile.read(length)
            try:
                return json.loads(body.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                self._send_error(400, "Invalid JSON body")
                return None

        def _parse_target(self) -> tuple[str, dict[str, list[str]]]:
            parsed = urlsplit(self.path)
            return parsed.path, parse_qs(parsed.query, keep_blank_values=True)

        def _query_value(
            self,
            query: dict[str, list[str]],
            key: str,
            *,
            default: Optional[str] = None,
            required: bool = False,
        ) -> Optional[str]:
            values = query.get(key)
            value = values[0] if values else default
            if required and (value is None or value == ""):
                raise ValueError(f"Missing query parameter: {key}")
            return value

        def _require_auth(self, query: Optional[dict[str, list[str]]] = None) -> bool:
            token = ""
            header = self.headers.get("Authorization", "")
            if header.startswith("Bearer "):
                token = header[len("Bearer ") :].strip()
            elif query is not None:
                token_values = query.get("token")
                if token_values:
                    token = token_values[0].strip()
            if not token:
                self._send_error(401, "Missing bearer token")
                return False
            if not state.verify_token(token):
                self._send_error(401, "Invalid or expired token")
                return False
            return True

        def _is_local_viewer(self) -> bool:
            client_ip = self.client_address[0].split("%")[0]
            if client_ip in state.local_ips:
                return True
            if client_ip.startswith("127."):
                return True
            if client_ip.startswith("::ffff:"):
                mapped = client_ip.split("::ffff:")[-1]
                return mapped in state.local_ips
            return False

        def _handle_challenge(self) -> None:
            nonce, ttl = state.issue_challenge()
            self._send_json(200, {"nonce": nonce, "expires_in": ttl})

        def _handle_login(self) -> None:
            body = self._read_json()
            if body is None:
                return
            password = body.get("password")
            if isinstance(password, str):
                if not state.verify_password(password):
                    self._send_error(403, "Authentication failed")
                    return
                token = state.issue_token()
                self._send_json(200, {"token": token, "expires_in": state.token_ttl})
                return
            nonce = body.get("nonce")
            proof = body.get("proof")
            if not isinstance(nonce, str) or not isinstance(proof, str):
                self._send_error(400, "password or (nonce + proof) is required")
                return
            if not state.verify_proof(nonce, proof):
                self._send_error(403, "Authentication failed")
                return
            token = state.issue_token()
            self._send_json(200, {"token": token, "expires_in": state.token_ttl})

        def _handle_refresh(self) -> None:
            token = state.issue_token()
            self._send_json(200, {"token": token, "expires_in": state.token_ttl})

        def _handle_server_passphrase(self) -> None:
            if not self._is_local_viewer():
                self._send_error(403, "Server passphrase is only visible on server machine")
                return
            self._send_json(
                200,
                {
                    "passphrase": state.passphrase,
                    "updated_at": now_ts(),
                },
            )

        def _handle_server_root(self) -> None:
            if not self._is_local_viewer():
                self._send_error(403, "Server root is only visible on server machine")
                return
            shared_root = state.get_shared_root()
            self._send_json(
                200,
                {
                    "root": str(shared_root),
                    "updated_at": now_ts(),
                },
            )

        def _handle_set_server_root(self) -> None:
            if not self._is_local_viewer():
                self._send_error(403, "Server root can only be changed on server machine")
                return
            body = self._read_json()
            if body is None:
                return
            new_root_raw = body.get("root")
            if not isinstance(new_root_raw, str) or not new_root_raw.strip():
                self._send_error(400, "root is required")
                return
            try:
                new_root = Path(new_root_raw).expanduser().resolve()
            except OSError as exc:
                self._send_error(400, f"Invalid root path: {exc}")
                return
            try:
                new_root.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self._send_error(400, f"Cannot create root directory: {exc}")
                return
            if not new_root.is_dir():
                self._send_error(400, "root path is not a directory")
                return
            previous_root = state.set_shared_root(new_root)
            self._send_json(
                200,
                {
                    "ok": True,
                    "root": str(new_root),
                    "previous_root": str(previous_root),
                    "updated_at": now_ts(),
                },
            )

        def _handle_pick_server_root(self) -> None:
            if not self._is_local_viewer():
                self._send_error(403, "Server root can only be changed on server machine")
                return
            current_root = state.get_shared_root()
            try:
                picked_root = pick_directory_dialog(current_root)
            except RuntimeError as exc:
                self._send_error(500, str(exc))
                return
            if picked_root is None:
                self._send_json(
                    200,
                    {
                        "ok": False,
                        "cancelled": True,
                        "root": str(current_root),
                        "updated_at": now_ts(),
                    },
                )
                return
            try:
                picked_root.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self._send_error(400, f"Cannot create root directory: {exc}")
                return
            if not picked_root.is_dir():
                self._send_error(400, "Selected path is not a directory")
                return
            previous_root = state.set_shared_root(picked_root)
            self._send_json(
                200,
                {
                    "ok": True,
                    "cancelled": False,
                    "root": str(picked_root),
                    "previous_root": str(previous_root),
                    "updated_at": now_ts(),
                },
            )

        def _handle_list(self, query: dict[str, list[str]]) -> None:
            shared_root = state.get_shared_root()
            try:
                raw_path = self._query_value(query, "path", default="") or ""
                target = resolve_safe_path(shared_root, raw_path, allow_root=True)
            except ValueError as exc:
                self._send_error(400, str(exc))
                return
            if not target.exists():
                self._send_error(404, "Directory does not exist")
                return
            if not target.is_dir():
                self._send_error(400, "Path is not a directory")
                return
            entries = []
            for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                stat = item.stat()
                rel_path = item.relative_to(shared_root).as_posix()
                entries.append(
                    {
                        "name": item.name,
                        "path": rel_path,
                        "type": "dir" if item.is_dir() else "file",
                        "size": int(stat.st_size) if item.is_file() else None,
                        "mtime": int(stat.st_mtime),
                    }
                )
            self._send_json(
                200,
                {
                    "base": normalize_remote_path(raw_path),
                    "entries": entries,
                },
            )

        def _handle_stat(self, query: dict[str, list[str]]) -> None:
            shared_root = state.get_shared_root()
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(shared_root, raw_path, allow_root=True)
            except ValueError as exc:
                self._send_error(400, str(exc))
                return
            if not target.exists():
                self._send_json(
                    200,
                    {
                        "path": normalize_remote_path(raw_path),
                        "exists": False,
                    },
                )
                return
            stat = target.stat()
            self._send_json(
                200,
                {
                    "path": normalize_remote_path(raw_path),
                    "exists": True,
                    "is_dir": target.is_dir(),
                    "size": int(stat.st_size),
                    "mtime": int(stat.st_mtime),
                },
            )

        def _handle_mkdir(self, query: dict[str, list[str]]) -> None:
            shared_root = state.get_shared_root()
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(shared_root, raw_path, allow_root=True)
            except ValueError as exc:
                self._send_error(400, str(exc))
                return
            if target.exists() and target.is_file():
                self._send_error(400, "A file already exists at this path")
                return
            target.mkdir(parents=True, exist_ok=True)
            self._send_json(
                200,
                {
                    "ok": True,
                    "path": normalize_remote_path(raw_path),
                },
            )

        def _handle_upload(self, query: dict[str, list[str]]) -> None:
            shared_root = state.get_shared_root()
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(shared_root, raw_path, allow_root=False)
            except ValueError as exc:
                self._send_error(400, str(exc))
                return
            if target.exists() and target.is_dir():
                self._send_error(400, "Cannot overwrite a directory")
                return
            content_length_header = self.headers.get("Content-Length")
            if content_length_header is None:
                self._send_error(411, "Content-Length is required")
                return
            try:
                content_length = int(content_length_header)
                offset = int(self.headers.get("X-Offset", "0"))
            except ValueError:
                self._send_error(400, "Invalid Content-Length or X-Offset")
                return
            if content_length < 0 or offset < 0:
                self._send_error(400, "Content-Length and X-Offset must be >= 0")
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            existing_size = target.stat().st_size if target.exists() else 0
            if offset > existing_size:
                self._send_error(409, f"Offset {offset} exceeds current size {existing_size}")
                return
            if offset == 0:
                mode = "wb"
            else:
                mode = "r+b"
            written = 0
            try:
                with target.open(mode, buffering=0) as f:
                    if offset > 0:
                        f.seek(offset)
                        if offset < existing_size:
                            f.truncate(offset)
                    remaining = content_length
                    while remaining:
                        chunk = self.rfile.read(min(IO_CHUNK, remaining))
                        if not chunk:
                            raise ConnectionError("Request body ended unexpectedly")
                        f.write(chunk)
                        written += len(chunk)
                        remaining -= len(chunk)
            except ConnectionError as exc:
                self._send_error(400, str(exc))
                return
            final_size = target.stat().st_size
            self._send_json(
                200,
                {
                    "ok": True,
                    "path": normalize_remote_path(raw_path),
                    "written": written,
                    "size": final_size,
                },
            )

        def _handle_download(self, query: dict[str, list[str]]) -> None:
            shared_root = state.get_shared_root()
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(shared_root, raw_path, allow_root=False)
            except ValueError as exc:
                self._send_error(400, str(exc))
                return
            if not target.exists() or not target.is_file():
                self._send_error(404, "File not found")
                return
            try:
                offset = int(self._query_value(query, "offset", default="0") or "0")
            except ValueError:
                self._send_error(400, "offset must be integer")
                return
            if offset < 0:
                self._send_error(400, "offset must be >= 0")
                return
            file_size = target.stat().st_size
            if offset > file_size:
                self._send_error(416, f"Offset {offset} exceeds file size {file_size}")
                return
            remaining = file_size - offset
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(remaining))
            self.send_header("X-File-Size", str(file_size))
            self.send_header("X-File-Name", target.name)
            self.send_header(
                "Content-Disposition",
                f"attachment; filename*=UTF-8''{quote(target.name, safe='')}",
            )
            self.send_header("Connection", "close")
            self.end_headers()

            with target.open("rb", buffering=0) as f:
                if offset:
                    f.seek(offset)
                sent_total = 0
                try:
                    if hasattr(self.connection, "sendfile") and remaining > 0:
                        while sent_total < remaining:
                            sent = self.connection.sendfile(
                                f,
                                count=remaining - sent_total,
                            )
                            if sent is None:
                                return
                            if sent == 0:
                                break
                            sent_total += sent
                    if sent_total < remaining:
                        while True:
                            chunk = f.read(IO_CHUNK)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return

        def _handle_asset(self, path: str) -> None:
            rel = path[len("/assets/") :].strip()
            if not rel or "/" in rel or "\\" in rel or ".." in rel:
                self._send_error(404, "Asset not found")
                return
            asset_file = ASSET_ROOT / rel
            if not asset_file.exists() or not asset_file.is_file():
                self._send_error(404, "Asset not found")
                return
            try:
                payload = asset_file.read_bytes()
            except OSError:
                self._send_error(500, "Failed to read asset")
                return
            guessed = mimetypes.guess_type(asset_file.name)[0]
            content_type = guessed or "application/octet-stream"
            self._send_bytes(200, payload, content_type)

        def do_GET(self) -> None:
            path, query = self._parse_target()
            if path in ("/", "/index.html"):
                self._send_html(200, WEB_UI_HTML)
                return
            if path.startswith("/assets/"):
                self._handle_asset(path)
                return
            if path == "/favicon.ico":
                self.send_response(204)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
                return
            if path == "/api/health":
                self._send_json(200, {"status": "ok", "server_time": now_ts()})
                return
            if path == "/api/challenge":
                self._handle_challenge()
                return
            if path == "/api/server-passphrase":
                self._handle_server_passphrase()
                return
            if path == "/api/server-root":
                self._handle_server_root()
                return
            if not path.startswith("/api/"):
                self._send_error(404, "Not found")
                return
            if not self._require_auth(query):
                return
            if path == "/api/list":
                self._handle_list(query)
            elif path == "/api/stat":
                self._handle_stat(query)
            elif path == "/api/download":
                self._handle_download(query)
            else:
                self._send_error(404, "Unknown endpoint")

        def do_POST(self) -> None:
            path, query = self._parse_target()
            if not path.startswith("/api/"):
                self._send_error(404, "Not found")
                return
            if path == "/api/login":
                self._handle_login()
                return
            if not self._require_auth():
                return
            if path == "/api/refresh":
                self._handle_refresh()
            elif path == "/api/upload":
                self._handle_upload(query)
            elif path == "/api/mkdir":
                self._handle_mkdir(query)
            elif path == "/api/server-root":
                self._handle_set_server_root()
            elif path == "/api/server-root/pick":
                self._handle_pick_server_root()
            else:
                self._send_error(404, "Unknown endpoint")

        def log_message(self, fmt: str, *args: object) -> None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            message = fmt % args
            sys.stderr.write(f"[{timestamp}] {self.client_address[0]} {message}\\n")

    return TransferHandler


class ClientError(RuntimeError):
    pass


def parse_server(server: str) -> tuple[str, int]:
    raw = server.strip()
    if "://" not in raw:
        raw = f"http://{raw}"
    parts = urlsplit(raw)
    if parts.scheme not in ("http", ""):
        raise ClientError("Only http:// is supported currently")
    if not parts.hostname:
        raise ClientError("Invalid --server format, expected host:port")
    port = parts.port or DEFAULT_PORT
    return parts.hostname, port


class LanTransferClient:
    # 命令行客户端：上传/下载/列表/建目录等操作。
    def __init__(self, server: str, password: str, timeout: float) -> None:
        self.host, self.port = parse_server(server)
        self.password = password.encode("utf-8")
        self.timeout = timeout
        self.token: Optional[str] = None

    def _new_connection(self) -> http.client.HTTPConnection:
        return http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)

    def _http_error(self, status: int, payload: bytes, default_reason: str) -> ClientError:
        try:
            data = json.loads(payload.decode("utf-8"))
            message = str(data.get("error", default_reason))
        except Exception:
            message = default_reason
        return ClientError(f"HTTP {status}: {message}")

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        payload: Optional[dict] = None,
    ) -> dict:
        conn = self._new_connection()
        headers = {"Connection": "close", "Accept": "application/json"}
        body = None
        if auth:
            self.ensure_token()
            headers["Authorization"] = f"Bearer {self.token}"
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
            headers["Content-Length"] = str(len(body))
        try:
            conn.request(method, path, body=body, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
        except OSError as exc:
            raise ClientError(f"Network error: {exc}") from exc
        finally:
            conn.close()
        if not (200 <= resp.status < 300):
            raise self._http_error(resp.status, raw, resp.reason)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ClientError("Server returned invalid JSON") from exc

    def ensure_token(self) -> None:
        if self.token:
            return
        challenge = self._request_json("GET", "/api/challenge", auth=False)
        nonce = challenge.get("nonce")
        if not isinstance(nonce, str):
            raise ClientError("Invalid challenge response")
        proof = hmac.new(
            self.password,
            nonce.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        login = self._request_json(
            "POST",
            "/api/login",
            auth=False,
            payload={"nonce": nonce, "proof": proof},
        )
        token = login.get("token")
        if not isinstance(token, str):
            raise ClientError("Invalid login response")
        self.token = token

    def stat(self, remote_path: str) -> dict:
        qp = quote_remote_path(remote_path)
        return self._request_json("GET", f"/api/stat?path={qp}")

    def list(self, remote_path: str = "") -> dict:
        qp = quote_remote_path(remote_path)
        return self._request_json("GET", f"/api/list?path={qp}")

    def mkdir(self, remote_path: str) -> dict:
        qp = quote_remote_path(remote_path)
        return self._request_json("POST", f"/api/mkdir?path={qp}")

    def upload(
        self,
        local_path: Path,
        remote_path: str,
        *,
        resume: bool,
        force: bool,
    ) -> dict:
        if not local_path.exists() or not local_path.is_file():
            raise ClientError(f"Local file does not exist: {local_path}")
        file_size = local_path.stat().st_size
        remote_info = self.stat(remote_path)
        offset = 0
        if remote_info.get("exists"):
            if remote_info.get("is_dir"):
                raise ClientError("Remote path points to a directory")
            remote_size = int(remote_info.get("size", 0))
            if force:
                offset = 0
            elif resume and 0 < remote_size < file_size:
                offset = remote_size
            elif remote_size == file_size:
                print("Remote file already complete, skipped.")
                return {"ok": True, "skipped": True, "size": file_size}
            elif remote_size > file_size:
                raise ClientError(
                    f"Remote file is larger ({remote_size}) than local ({file_size}). "
                    "Use --force to overwrite."
                )
        self.ensure_token()
        to_send = file_size - offset
        request_path = f"/api/upload?path={quote_remote_path(remote_path)}"
        conn = self._new_connection()
        start_time = time.time()
        sent = 0
        try:
            conn.putrequest("POST", request_path)
            conn.putheader("Authorization", f"Bearer {self.token}")
            conn.putheader("Connection", "close")
            conn.putheader("Content-Type", "application/octet-stream")
            conn.putheader("Content-Length", str(to_send))
            conn.putheader("X-Offset", str(offset))
            conn.endheaders()
            with local_path.open("rb", buffering=0) as src:
                src.seek(offset)
                while sent < to_send:
                    chunk = src.read(min(IO_CHUNK, to_send - sent))
                    if not chunk:
                        break
                    conn.send(chunk)
                    sent += len(chunk)
                    self._print_progress(
                        "Uploading",
                        current=offset + sent,
                        total=file_size,
                        moved=sent,
                        started_at=start_time,
                    )
            if to_send == 0:
                self._print_progress(
                    "Uploading",
                    current=file_size,
                    total=file_size,
                    moved=0,
                    started_at=start_time,
                )
            resp = conn.getresponse()
            raw = resp.read()
        except OSError as exc:
            raise ClientError(f"Upload failed due to network error: {exc}") from exc
        finally:
            conn.close()
        print()
        if not (200 <= resp.status < 300):
            raise self._http_error(resp.status, raw, resp.reason)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ClientError("Server returned invalid JSON after upload") from exc

    def download(
        self,
        remote_path: str,
        local_path: Path,
        *,
        resume: bool,
        force: bool,
    ) -> None:
        info = self.stat(remote_path)
        if not info.get("exists"):
            raise ClientError("Remote file does not exist")
        if info.get("is_dir"):
            raise ClientError("Remote path is a directory")
        remote_size = int(info.get("size", 0))
        offset = 0
        if local_path.exists():
            if local_path.is_dir():
                raise ClientError(f"Local path is a directory: {local_path}")
            local_size = local_path.stat().st_size
            if force:
                offset = 0
            elif resume and 0 < local_size < remote_size:
                offset = local_size
            elif local_size == remote_size:
                print("Local file already complete, skipped.")
                return
            elif local_size > remote_size:
                raise ClientError(
                    f"Local file is larger ({local_size}) than remote ({remote_size}). "
                    "Use --force to overwrite."
                )
        self.ensure_token()
        request_path = (
            f"/api/download?path={quote_remote_path(remote_path)}&offset={offset}"
        )
        conn = self._new_connection()
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Connection": "close",
        }
        start_time = time.time()
        moved = 0
        mode = "ab" if offset > 0 else "wb"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            conn.request("GET", request_path, headers=headers)
            resp = conn.getresponse()
            if not (200 <= resp.status < 300):
                raw = resp.read()
                raise self._http_error(resp.status, raw, resp.reason)
            with local_path.open(mode, buffering=0) as dst:
                while True:
                    chunk = resp.read(IO_CHUNK)
                    if not chunk:
                        break
                    dst.write(chunk)
                    moved += len(chunk)
                    self._print_progress(
                        "Downloading",
                        current=offset + moved,
                        total=remote_size,
                        moved=moved,
                        started_at=start_time,
                    )
            if remote_size == 0:
                self._print_progress(
                    "Downloading",
                    current=0,
                    total=0,
                    moved=0,
                    started_at=start_time,
                )
        except OSError as exc:
            raise ClientError(f"Download failed due to network error: {exc}") from exc
        finally:
            conn.close()
        print()
        final_size = local_path.stat().st_size
        if final_size != remote_size:
            raise ClientError(
                f"Download incomplete: local size {final_size}, expected {remote_size}"
            )

    @staticmethod
    def _print_progress(
        action: str,
        *,
        current: int,
        total: int,
        moved: int,
        started_at: float,
    ) -> None:
        elapsed = max(time.time() - started_at, 1e-6)
        speed = moved / elapsed
        if total > 0:
            percent = current * 100.0 / total
            progress = f"{percent:6.2f}% {format_bytes(current)}/{format_bytes(total)}"
        else:
            progress = "100.00% 0 B/0 B"
        text = f"\\r{action}: {progress}  {format_bytes(speed)}/s"
        sys.stdout.write(text)
        sys.stdout.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LAN file transfer tool with web login, resumable transfer, and local-network speed."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Run transfer server")
    serve.add_argument(
        "--bind",
        default="auto",
        help="Bind address (default: auto -> detected LAN IP)",
    )
    serve.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (default: 9000)")
    serve.add_argument(
        "--root",
        default="./shared",
        help="Shared directory path (default: ./shared)",
    )
    serve.add_argument(
        "--password",
        help="Server passphrase (if omitted, one is auto-generated at startup)",
    )
    serve.add_argument(
        "--token-ttl",
        type=int,
        default=DEFAULT_TOKEN_TTL,
        help=f"Token ttl in seconds (default: {DEFAULT_TOKEN_TTL})",
    )
    serve.add_argument(
        "--challenge-ttl",
        type=int,
        default=DEFAULT_CHALLENGE_TTL,
        help="Challenge ttl in seconds (default: 60)",
    )
    serve.add_argument(
        "--port-conflict",
        choices=["ask", "kill", "abort"],
        default="ask",
        help="What to do when port is occupied: ask/kill/abort (default: ask)",
    )

    def add_client_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--server", required=True, help="Server address, e.g. 192.168.1.10:9000")
        p.add_argument("--password", help="Server password")
        p.add_argument(
            "--timeout",
            type=float,
            default=DEFAULT_TIMEOUT,
            help="Network timeout in seconds (default: 30)",
        )

    upload = subparsers.add_parser("upload", help="Upload one file")
    add_client_common(upload)
    upload.add_argument("local_path", help="Local file path")
    upload.add_argument(
        "remote_path",
        nargs="?",
        help="Remote file path (default: local file name)",
    )
    upload.add_argument(
        "--no-resume",
        action="store_true",
        help="Disable resume and start from offset 0",
    )
    upload.add_argument(
        "--force",
        action="store_true",
        help="Overwrite remote file if exists",
    )

    download = subparsers.add_parser("download", help="Download one file")
    add_client_common(download)
    download.add_argument("remote_path", help="Remote file path")
    download.add_argument(
        "local_path",
        nargs="?",
        help="Local file path (default: remote file name)",
    )
    download.add_argument(
        "--no-resume",
        action="store_true",
        help="Disable resume and start from offset 0",
    )
    download.add_argument(
        "--force",
        action="store_true",
        help="Overwrite local file if exists",
    )

    list_cmd = subparsers.add_parser("list", help="List remote directory")
    add_client_common(list_cmd)
    list_cmd.add_argument("remote_path", nargs="?", default="", help="Remote directory path")

    stat_cmd = subparsers.add_parser("stat", help="Show remote path metadata")
    add_client_common(stat_cmd)
    stat_cmd.add_argument("remote_path", help="Remote path")

    mkdir_cmd = subparsers.add_parser("mkdir", help="Create remote directory")
    add_client_common(mkdir_cmd)
    mkdir_cmd.add_argument("remote_path", help="Remote directory path")

    return parser


def generate_passphrase(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        candidate = "".join(secrets.choice(alphabet) for _ in range(length))
        has_alpha = any(ch.isalpha() for ch in candidate)
        has_digit = any(ch.isdigit() for ch in candidate)
        if has_alpha and has_digit:
            return candidate


def resolve_server_password(cli_password: Optional[str]) -> tuple[str, bool]:
    if cli_password:
        return cli_password, False
    env_password = os.getenv("LAN_TRANSFER_PASSWORD")
    if env_password:
        return env_password, False
    return generate_passphrase(6), True


def get_client_password(cli_password: Optional[str], prompt: str) -> str:
    if cli_password:
        return cli_password
    env_password = os.getenv("LAN_TRANSFER_PASSWORD")
    if env_password:
        return env_password
    return getpass.getpass(prompt)


def run_server(args: argparse.Namespace) -> int:
    password, generated = resolve_server_password(args.password)
    bind_host = detect_lan_ip() if str(args.bind).lower() == "auto" else args.bind
    shared_root = Path(args.root).expanduser().resolve()
    shared_root.mkdir(parents=True, exist_ok=True)
    state = ServerState(
        shared_root=shared_root,
        password_key=password.encode("utf-8"),
        passphrase=password,
        token_ttl=args.token_ttl,
        challenge_ttl=args.challenge_ttl,
    )
    state.local_ips.add(str(bind_host).split("%")[0])
    handler = make_handler(state)
    try:
        httpd = ThreadingHTTPServer((bind_host, args.port), handler)
    except OSError as exc:
        winerror = getattr(exc, "winerror", None)
        errno = getattr(exc, "errno", None)
        address_in_use = winerror == 10048 or errno in (48, 98)
        retried = False
        if address_in_use:
            pids = find_listening_pids(args.port)
            if pids:
                action = args.port_conflict
                should_kill = False
                if action == "kill":
                    should_kill = True
                elif action == "ask":
                    if sys.stdin.isatty():
                        print(
                            f"Port {args.port} is occupied by PID(s): "
                            + ", ".join(str(pid) for pid in pids)
                        )
                        answer = (
                            input("Kill these processes and retry? [y/N]: ")
                            .strip()
                            .lower()
                        )
                        should_kill = answer in {"y", "yes"}
                    else:
                        print(
                            "Port is occupied and interactive prompt is unavailable. "
                            "Use --port-conflict kill to auto-terminate.",
                            file=sys.stderr,
                        )
                if should_kill:
                    killed = kill_processes(pids)
                    if killed:
                        time.sleep(0.4)
                        retried = True
                        try:
                            httpd = ThreadingHTTPServer((bind_host, args.port), handler)
                        except OSError:
                            pass
        if not retried or "httpd" not in locals():
            print(f"Failed to bind {bind_host}:{args.port}: {exc}", file=sys.stderr)
            print(
                "Port may already be used by an old process. "
                f"Check with: netstat -ano | findstr :{args.port}",
                file=sys.stderr,
            )
            return 1
    httpd.daemon_threads = True
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    detected_ip = detect_lan_ip()
    access_host = detected_ip if bind_host in ("0.0.0.0", "::") else bind_host
    open_url = f"http://{access_host}:{args.port}/"
    print(
        f"Server started on {bind_host}:{args.port}\n"
        "Open in browser:"
        f"{open_url}\n"
        f"PID: {os.getpid()}\n"
        f"Shared directory: {shared_root}\n"
        "Press Ctrl+C to stop."
    )
    if generated:
        print(f"Generated passphrase: {password}")
    print(f"Token lifetime: {state.token_ttl // 3600} hours")
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        httpd.server_close()
    return 0


def create_client(args: argparse.Namespace) -> LanTransferClient:
    password = get_client_password(args.password, "Enter server password: ")
    return LanTransferClient(args.server, password=password, timeout=args.timeout)


def run_client(args: argparse.Namespace) -> int:
    client = create_client(args)
    if args.command == "list":
        result = client.list(args.remote_path)
        base = result.get("base") or "/"
        entries = result.get("entries", [])
        print(f"Remote directory: {base}")
        if not entries:
            print("(empty)")
            return 0
        for item in entries:
            item_type = item.get("type", "?")
            path = item.get("path", item.get("name", ""))
            size = item.get("size")
            size_text = "<DIR>" if item_type == "dir" else format_bytes(int(size or 0))
            print(f"{item_type.upper():<4}  {size_text:>12}  {path}")
        return 0

    if args.command == "stat":
        result = client.stat(args.remote_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "mkdir":
        result = client.mkdir(args.remote_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "upload":
        local_path = Path(args.local_path).expanduser().resolve()
        remote_path = normalize_remote_path(args.remote_path or local_path.name)
        result = client.upload(
            local_path=local_path,
            remote_path=remote_path,
            resume=not args.no_resume,
            force=args.force,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "download":
        remote_path = normalize_remote_path(args.remote_path)
        if args.local_path:
            local_path = Path(args.local_path).expanduser().resolve()
        else:
            local_name = Path(remote_path).name
            if not local_name:
                raise ClientError("Please provide local_path for directory download")
            local_path = Path.cwd() / local_name
        client.download(
            remote_path=remote_path,
            local_path=local_path,
            resume=not args.no_resume,
            force=args.force,
        )
        print(
            json.dumps(
                {
                    "ok": True,
                    "remote_path": remote_path,
                    "local_path": str(local_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    raise ClientError(f"Unsupported command: {args.command}")


def main() -> int:
    if len(sys.argv) == 1:
        default_args = argparse.Namespace(
            command="serve",
            bind="auto",
            port=DEFAULT_PORT,
            root="./shared",
            password=None,
            token_ttl=DEFAULT_TOKEN_TTL,
            challenge_ttl=DEFAULT_CHALLENGE_TTL,
            port_conflict="ask",
        )
        return run_server(default_args)
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "serve":
            return run_server(args)
        return run_client(args)
    except ClientError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
