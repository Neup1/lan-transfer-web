#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import getpass
import hashlib
import hmac
import http.client
import json
import os
import secrets
import socket
import sys
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import parse_qs, quote, urlsplit


IO_CHUNK = 4 * 1024 * 1024
DEFAULT_PORT = 9000
DEFAULT_TIMEOUT = 30.0
DEFAULT_TOKEN_TTL = 24 * 3600
DEFAULT_CHALLENGE_TTL = 60
JSON_LIMIT = 1024 * 1024

WEB_UI_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LAN Transfer</title>
  <style>
    :root {
      --bg: #f3f6fb;
      --surface: #ffffff;
      --surface-soft: #f8fafe;
      --border: #dbe5f1;
      --text: #243245;
      --muted: #607188;
      --accent: #2f6fdf;
      --accent-soft: #eaf2ff;
      --danger: #c73a50;
      --danger-soft: #ffecef;
      --radius-lg: 18px;
      --radius-md: 12px;
      --radius-sm: 10px;
      --shadow: 0 20px 44px rgba(30, 52, 85, 0.10);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at 14% 10%, #e8f0ff 0%, rgba(232, 240, 255, 0) 40%),
        radial-gradient(circle at 88% 88%, #edf9f4 0%, rgba(237, 249, 244, 0) 32%),
        var(--bg);
      display: flex;
      justify-content: center;
      padding: 28px 18px;
    }
    .shell {
      width: min(1100px, 100%);
      display: grid;
      gap: 18px;
      grid-template-columns: 320px 1fr;
    }
    .card {
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      background: var(--surface);
      box-shadow: var(--shadow);
    }
    .side {
      padding: 20px;
      display: grid;
      gap: 16px;
      align-content: start;
      position: sticky;
      top: 14px;
      height: fit-content;
    }
    .headline {
      display: grid;
      gap: 8px;
    }
    .headline h1 {
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
      font-weight: 700;
      letter-spacing: 0.2px;
    }
    .headline p {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }
    .field {
      display: grid;
      gap: 8px;
    }
    .field label {
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }
    input[type="password"],
    input[type="text"] {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 10px 12px;
      outline: none;
      font-size: 14px;
      color: var(--text);
      background: #fff;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    input[type="password"]:focus,
    input[type="text"]:focus {
      border-color: #87aaf6;
      box-shadow: 0 0 0 4px #edf3ff;
    }
    button {
      border: 1px solid transparent;
      border-radius: var(--radius-md);
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      font-size: 14px;
      padding: 10px 14px;
      cursor: pointer;
      transition: transform 0.08s ease, box-shadow 0.2s ease, opacity 0.2s ease;
      box-shadow: 0 10px 18px rgba(47, 111, 223, 0.25);
    }
    button:hover { transform: translateY(-1px); }
    button:active { transform: translateY(0); }
    button:disabled { opacity: 0.55; cursor: not-allowed; }
    button.ghost {
      color: var(--text);
      background: #fff;
      border-color: var(--border);
      box-shadow: none;
    }
    button.soft {
      color: var(--accent);
      background: var(--accent-soft);
      border-color: #d3e4ff;
      box-shadow: none;
    }
    .status {
      min-height: 52px;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: var(--surface-soft);
      padding: 10px 12px;
      font-size: 13px;
      line-height: 1.5;
      color: var(--muted);
      word-break: break-word;
    }
    .status.error {
      border-color: #f1b9c3;
      background: var(--danger-soft);
      color: var(--danger);
    }
    .status.ok {
      border-color: #bde6ce;
      background: #eefbf3;
      color: #21784b;
    }
    .main {
      padding: 20px;
      display: grid;
      gap: 14px;
      align-content: start;
      min-height: 600px;
    }
    .toolbar {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto auto;
      align-items: center;
    }
    .path-chip {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      padding: 10px 12px;
      overflow-x: auto;
      white-space: nowrap;
      font-size: 13px;
    }
    .crumb {
      border: none;
      background: transparent;
      color: var(--accent);
      padding: 0;
      margin: 0;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      box-shadow: none;
    }
    .crumb + .crumb::before {
      content: "/";
      color: #8ca0bb;
      margin: 0 7px 0 6px;
      font-weight: 400;
    }
    .action-grid {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
    }
    .upload-row {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      padding: 10px 12px;
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .upload-row input[type="file"] {
      width: 100%;
      font-size: 13px;
      color: var(--muted);
    }
    .upload-option {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      margin-top: 4px;
    }
    .upload-option input {
      accent-color: var(--accent);
    }
    .table-wrap {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      overflow: hidden;
      background: #fff;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 12px 10px;
      border-bottom: 1px solid #ecf1f7;
      font-size: 13px;
      text-align: left;
      vertical-align: middle;
    }
    th {
      color: #4f637d;
      background: #f8fbff;
      font-weight: 700;
    }
    tr:last-child td { border-bottom: none; }
    .name-cell {
      max-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .type-pill {
      display: inline-block;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 9px;
      border: 1px solid var(--border);
      color: var(--muted);
      background: #fff;
    }
    .type-pill.dir {
      background: #edf6ff;
      border-color: #cfe4ff;
      color: #2b67bf;
    }
    .actions {
      display: flex;
      gap: 6px;
      justify-content: flex-end;
    }
    .empty {
      padding: 34px 20px;
      text-align: center;
      color: var(--muted);
      font-size: 14px;
    }
    .inline {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .tiny {
      font-size: 12px;
      color: var(--muted);
    }
    @media (max-width: 960px) {
      .shell { grid-template-columns: 1fr; }
      .side { position: static; }
      .toolbar { grid-template-columns: 1fr; }
      .action-grid { grid-template-columns: 1fr; }
      .upload-row { grid-template-columns: 1fr; }
      th:nth-child(3),
      td:nth-child(3),
      th:nth-child(4),
      td:nth-child(4) { display: none; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="card side">
      <div class="headline">
        <h1>LAN Transfer</h1>
        <p>Fast local network file transfer with password authentication.</p>
      </div>
      <div class="field">
        <label for="passwordInput">Password</label>
        <input id="passwordInput" type="password" placeholder="Enter server password">
      </div>
      <div class="inline">
        <button id="loginBtn">Sign In</button>
        <button id="logoutBtn" class="ghost">Sign Out</button>
      </div>
      <div id="status" class="status">Not signed in.</div>
      <div class="tiny">Tip: This page works best when opened from the same host running the server.</div>
    </aside>
    <main class="card main">
      <div class="toolbar">
        <div id="breadcrumbs" class="path-chip"></div>
        <button id="refreshBtn" class="soft">Refresh</button>
        <button id="upBtn" class="ghost">Up</button>
      </div>

      <div class="action-grid">
        <div>
          <div class="upload-row">
            <input id="uploadInput" type="file" multiple>
            <button id="uploadBtn">Upload</button>
          </div>
          <label class="upload-option">
            <input id="resumeCheckbox" type="checkbox" checked>
            Resume if same file already exists
          </label>
        </div>
        <div class="upload-row">
          <input id="mkdirInput" type="text" placeholder="New folder name">
          <button id="mkdirBtn" class="soft">Create Folder</button>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th style="width: 44%;">Name</th>
              <th style="width: 11%;">Type</th>
              <th style="width: 15%;">Size</th>
              <th style="width: 18%;">Modified</th>
              <th style="width: 12%; text-align: right;">Actions</th>
            </tr>
          </thead>
          <tbody id="fileBody">
            <tr>
              <td colspan="5" class="empty">Sign in to load files.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>

  <script>
    const tokenKey = "lan_transfer_token";
    const state = {
      token: sessionStorage.getItem(tokenKey) || "",
      path: "",
      entries: []
    };

    const $ = (sel) => document.querySelector(sel);
    const statusEl = $("#status");
    const passwordInput = $("#passwordInput");
    const loginBtn = $("#loginBtn");
    const logoutBtn = $("#logoutBtn");
    const refreshBtn = $("#refreshBtn");
    const upBtn = $("#upBtn");
    const uploadInput = $("#uploadInput");
    const uploadBtn = $("#uploadBtn");
    const mkdirInput = $("#mkdirInput");
    const mkdirBtn = $("#mkdirBtn");
    const resumeCheckbox = $("#resumeCheckbox");
    const breadcrumbs = $("#breadcrumbs");
    const fileBody = $("#fileBody");

    function setStatus(text, kind = "") {
      statusEl.textContent = text;
      statusEl.className = "status" + (kind ? " " + kind : "");
    }

    function setToken(token) {
      state.token = token || "";
      if (state.token) {
        sessionStorage.setItem(tokenKey, state.token);
      } else {
        sessionStorage.removeItem(tokenKey);
      }
    }

    function formatBytes(size) {
      const units = ["B", "KiB", "MiB", "GiB", "TiB"];
      let value = Number(size || 0);
      let idx = 0;
      while (value >= 1024 && idx < units.length - 1) {
        value /= 1024;
        idx += 1;
      }
      if (idx === 0) {
        return String(Math.round(value)) + " " + units[idx];
      }
      return value.toFixed(2) + " " + units[idx];
    }

    function formatTime(epoch) {
      if (!epoch) return "-";
      const d = new Date(Number(epoch) * 1000);
      return d.toLocaleString();
    }

    function joinPath(base, name) {
      const b = (base || "").replace(/^\/+|\/+$/g, "");
      const n = (name || "").replace(/^\/+|\/+$/g, "");
      if (!b) return n;
      if (!n) return b;
      return b + "/" + n;
    }

    function parentPath(path) {
      const clean = (path || "").replace(/^\/+|\/+$/g, "");
      if (!clean) return "";
      const parts = clean.split("/");
      parts.pop();
      return parts.join("/");
    }

    function clearTable(message) {
      fileBody.innerHTML = "";
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 5;
      cell.className = "empty";
      cell.textContent = message;
      row.appendChild(cell);
      fileBody.appendChild(row);
    }

    function renderBreadcrumbs() {
      breadcrumbs.innerHTML = "";
      const rootBtn = document.createElement("button");
      rootBtn.className = "crumb";
      rootBtn.textContent = "root";
      rootBtn.addEventListener("click", () => loadDir(""));
      breadcrumbs.appendChild(rootBtn);

      const clean = (state.path || "").replace(/^\/+|\/+$/g, "");
      if (!clean) return;

      const parts = clean.split("/");
      let cursor = "";
      for (const part of parts) {
        cursor = joinPath(cursor, part);
        const btn = document.createElement("button");
        btn.className = "crumb";
        btn.textContent = part;
        btn.addEventListener("click", () => loadDir(cursor));
        breadcrumbs.appendChild(btn);
      }
    }

    async function requestJson(path, options = {}) {
      const headers = new Headers(options.headers || {});
      headers.set("Accept", "application/json");
      if (state.token) {
        headers.set("Authorization", "Bearer " + state.token);
      }
      const response = await fetch(path, {
        ...options,
        headers
      });
      if (response.status === 401) {
        setToken("");
        throw new Error("Authentication expired. Please sign in again.");
      }
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || ("HTTP " + response.status));
      }
      return data;
    }

    async function hmacHex(secret, message) {
      if (!window.crypto || !window.crypto.subtle) {
        throw new Error("Browser does not support crypto.subtle.");
      }
      const encoder = new TextEncoder();
      const key = await window.crypto.subtle.importKey(
        "raw",
        encoder.encode(secret),
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign"]
      );
      const signature = await window.crypto.subtle.sign("HMAC", key, encoder.encode(message));
      return Array.from(new Uint8Array(signature))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
    }

    async function signIn() {
      const password = passwordInput.value;
      if (!password) {
        setStatus("Please enter password first.", "error");
        return;
      }
      loginBtn.disabled = true;
      try {
        setStatus("Requesting challenge...");
        const challenge = await requestJson("/api/challenge");
        const proof = await hmacHex(password, challenge.nonce);
        const login = await requestJson("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ nonce: challenge.nonce, proof })
        });
        setToken(login.token || "");
        passwordInput.value = "";
        setStatus("Signed in. Loading files...", "ok");
        await loadDir(state.path || "");
      } catch (err) {
        setStatus(String(err.message || err), "error");
      } finally {
        loginBtn.disabled = false;
      }
    }

    function signOut() {
      setToken("");
      clearTable("Sign in to load files.");
      setStatus("Signed out.");
    }

    async function loadDir(path) {
      if (!state.token) {
        clearTable("Sign in to load files.");
        renderBreadcrumbs();
        return;
      }
      const query = encodeURIComponent(path || "");
      const result = await requestJson("/api/list?path=" + query);
      state.path = result.base || "";
      state.entries = Array.isArray(result.entries) ? result.entries : [];
      renderBreadcrumbs();
      renderFiles();
    }

    function renderFiles() {
      if (!state.entries.length) {
        clearTable("This folder is empty.");
        return;
      }
      fileBody.innerHTML = "";
      for (const item of state.entries) {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.className = "name-cell";
        nameCell.textContent = item.name || "";
        row.appendChild(nameCell);

        const typeCell = document.createElement("td");
        const typePill = document.createElement("span");
        typePill.className = "type-pill " + (item.type === "dir" ? "dir" : "");
        typePill.textContent = item.type === "dir" ? "Folder" : "File";
        typeCell.appendChild(typePill);
        row.appendChild(typeCell);

        const sizeCell = document.createElement("td");
        sizeCell.textContent = item.type === "dir" ? "-" : formatBytes(item.size);
        row.appendChild(sizeCell);

        const timeCell = document.createElement("td");
        timeCell.textContent = formatTime(item.mtime);
        row.appendChild(timeCell);

        const actionCell = document.createElement("td");
        actionCell.className = "actions";
        if (item.type === "dir") {
          const openBtn = document.createElement("button");
          openBtn.className = "soft";
          openBtn.textContent = "Open";
          openBtn.addEventListener("click", () => {
            loadDir(item.path || "");
          });
          actionCell.appendChild(openBtn);
        } else {
          const downloadBtn = document.createElement("button");
          downloadBtn.className = "ghost";
          downloadBtn.textContent = "Download";
          downloadBtn.addEventListener("click", () => triggerDownload(item.path || "", item.name || "download"));
          actionCell.appendChild(downloadBtn);
        }
        row.appendChild(actionCell);

        fileBody.appendChild(row);
      }
    }

    function triggerDownload(remotePath, fileName) {
      if (!state.token) {
        setStatus("Please sign in first.", "error");
        return;
      }
      const url = "/api/download?path=" + encodeURIComponent(remotePath) + "&token=" + encodeURIComponent(state.token);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName || "";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setStatus("Download started: " + remotePath, "ok");
    }

    async function queryRemoteOffset(remotePath, fileSize, allowResume) {
      const stat = await requestJson("/api/stat?path=" + encodeURIComponent(remotePath));
      if (!stat.exists) return 0;
      if (stat.is_dir) throw new Error("Remote target is a folder: " + remotePath);
      const remoteSize = Number(stat.size || 0);
      if (!allowResume) return 0;
      if (remoteSize === fileSize) return fileSize;
      if (remoteSize > 0 && remoteSize < fileSize) return remoteSize;
      return 0;
    }

    function uploadChunk(file, remotePath, offset, onProgress) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/upload?path=" + encodeURIComponent(remotePath), true);
        xhr.setRequestHeader("Authorization", "Bearer " + state.token);
        xhr.setRequestHeader("X-Offset", String(offset));
        xhr.setRequestHeader("Content-Type", "application/octet-stream");

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            onProgress(offset + event.loaded, file.size);
          }
        };

        xhr.onerror = () => reject(new Error("Network error during upload."));
        xhr.onload = () => {
          if (xhr.status === 401) {
            setToken("");
            reject(new Error("Authentication expired. Please sign in again."));
            return;
          }
          if (xhr.status < 200 || xhr.status >= 300) {
            let msg = "Upload failed with HTTP " + xhr.status;
            try {
              const payload = JSON.parse(xhr.responseText || "{}");
              if (payload.error) msg = payload.error;
            } catch (ignore) {
            }
            reject(new Error(msg));
            return;
          }
          onProgress(file.size, file.size);
          resolve();
        };

        const payload = offset > 0 ? file.slice(offset) : file;
        xhr.send(payload);
      });
    }

    async function uploadSelectedFiles() {
      const files = Array.from(uploadInput.files || []);
      if (!files.length) {
        setStatus("Choose files first.", "error");
        return;
      }
      if (!state.token) {
        setStatus("Please sign in first.", "error");
        return;
      }
      uploadBtn.disabled = true;
      let done = 0;
      try {
        for (const file of files) {
          const remotePath = joinPath(state.path, file.name);
          const allowResume = Boolean(resumeCheckbox.checked);
          const offset = await queryRemoteOffset(remotePath, file.size, allowResume);
          if (offset === file.size) {
            done += 1;
            setStatus("Skipped existing file: " + file.name + " (" + done + "/" + files.length + ")", "ok");
            continue;
          }
          await uploadChunk(file, remotePath, offset, (current, total) => {
            const pct = total > 0 ? ((current * 100) / total).toFixed(2) : "100.00";
            setStatus("Uploading " + file.name + " " + pct + "% (" + done + "/" + files.length + ")");
          });
          done += 1;
          setStatus("Uploaded: " + file.name + " (" + done + "/" + files.length + ")", "ok");
        }
        uploadInput.value = "";
        await loadDir(state.path);
      } catch (err) {
        setStatus(String(err.message || err), "error");
      } finally {
        uploadBtn.disabled = false;
      }
    }

    async function createFolder() {
      const name = (mkdirInput.value || "").trim();
      if (!name) {
        setStatus("Please enter folder name.", "error");
        return;
      }
      if (!state.token) {
        setStatus("Please sign in first.", "error");
        return;
      }
      try {
        const remotePath = joinPath(state.path, name);
        await requestJson("/api/mkdir?path=" + encodeURIComponent(remotePath), { method: "POST" });
        mkdirInput.value = "";
        setStatus("Folder created: " + name, "ok");
        await loadDir(state.path);
      } catch (err) {
        setStatus(String(err.message || err), "error");
      }
    }

    loginBtn.addEventListener("click", signIn);
    logoutBtn.addEventListener("click", signOut);
    refreshBtn.addEventListener("click", async () => {
      try {
        await loadDir(state.path);
        setStatus("Refreshed.", "ok");
      } catch (err) {
        setStatus(String(err.message || err), "error");
      }
    });
    upBtn.addEventListener("click", async () => {
      try {
        await loadDir(parentPath(state.path));
      } catch (err) {
        setStatus(String(err.message || err), "error");
      }
    });
    uploadBtn.addEventListener("click", uploadSelectedFiles);
    mkdirBtn.addEventListener("click", createFolder);
    mkdirInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        createFolder();
      }
    });
    passwordInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        signIn();
      }
    });

    (async () => {
      renderBreadcrumbs();
      if (!state.token) {
        clearTable("Sign in to load files.");
        return;
      }
      try {
        setStatus("Restoring session...");
        await loadDir("");
        setStatus("Signed in. Ready.", "ok");
      } catch (err) {
        setToken("");
        clearTable("Sign in to load files.");
        setStatus(String(err.message || err), "error");
      }
    })();
  </script>
</body>
</html>
"""


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def now_ts() -> int:
    return int(time.time())


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
    shared_root: Path
    password_key: bytes
    token_ttl: int = DEFAULT_TOKEN_TTL
    challenge_ttl: int = DEFAULT_CHALLENGE_TTL
    token_secret: bytes = field(default_factory=lambda: secrets.token_bytes(32))
    challenges: Dict[str, float] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

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

    def issue_token(self) -> str:
        payload = {
            "v": 1,
            "iat": now_ts(),
            "exp": now_ts() + self.token_ttl,
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

        def _handle_challenge(self) -> None:
            nonce, ttl = state.issue_challenge()
            self._send_json(200, {"nonce": nonce, "expires_in": ttl})

        def _handle_login(self) -> None:
            body = self._read_json()
            if body is None:
                return
            nonce = body.get("nonce")
            proof = body.get("proof")
            if not isinstance(nonce, str) or not isinstance(proof, str):
                self._send_error(400, "nonce and proof must be strings")
                return
            if not state.verify_proof(nonce, proof):
                self._send_error(403, "Authentication failed")
                return
            token = state.issue_token()
            self._send_json(200, {"token": token, "expires_in": state.token_ttl})

        def _handle_list(self, query: dict[str, list[str]]) -> None:
            try:
                raw_path = self._query_value(query, "path", default="") or ""
                target = resolve_safe_path(state.shared_root, raw_path, allow_root=True)
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
                rel_path = item.relative_to(state.shared_root).as_posix()
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
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(state.shared_root, raw_path, allow_root=True)
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
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(state.shared_root, raw_path, allow_root=True)
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
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(state.shared_root, raw_path, allow_root=False)
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
            try:
                raw_path = self._query_value(query, "path", required=True) or ""
                target = resolve_safe_path(state.shared_root, raw_path, allow_root=False)
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

        def do_GET(self) -> None:
            path, query = self._parse_target()
            if path in ("/", "/index.html"):
                self._send_html(200, WEB_UI_HTML)
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
            if path == "/api/upload":
                self._handle_upload(query)
            elif path == "/api/mkdir":
                self._handle_mkdir(query)
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
        description="LAN file transfer tool with password auth and resumable transport."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve = subparsers.add_parser("serve", help="Run transfer server")
    serve.add_argument("--bind", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    serve.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port (default: 9000)")
    serve.add_argument(
        "--root",
        default="./shared",
        help="Shared directory path (default: ./shared)",
    )
    serve.add_argument("--password", help="Server password")
    serve.add_argument(
        "--token-ttl",
        type=int,
        default=DEFAULT_TOKEN_TTL,
        help="Token ttl in seconds (default: 86400)",
    )
    serve.add_argument(
        "--challenge-ttl",
        type=int,
        default=DEFAULT_CHALLENGE_TTL,
        help="Challenge ttl in seconds (default: 60)",
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


def get_password(cli_password: Optional[str], prompt: str) -> str:
    if cli_password:
        return cli_password
    env_password = os.getenv("LAN_TRANSFER_PASSWORD")
    if env_password:
        return env_password
    return getpass.getpass(prompt)


def run_server(args: argparse.Namespace) -> int:
    password = get_password(args.password, "Set server password: ")
    shared_root = Path(args.root).expanduser().resolve()
    shared_root.mkdir(parents=True, exist_ok=True)
    state = ServerState(
        shared_root=shared_root,
        password_key=password.encode("utf-8"),
        token_ttl=args.token_ttl,
        challenge_ttl=args.challenge_ttl,
    )
    handler = make_handler(state)
    httpd = ThreadingHTTPServer((args.bind, args.port), handler)
    httpd.daemon_threads = True
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(
        f"Server started on {args.bind}:{args.port}\\n"
        f"Shared directory: {shared_root}\\n"
        "Press Ctrl+C to stop."
    )
    try:
        httpd.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\\nShutting down...")
    finally:
        httpd.server_close()
    return 0


def create_client(args: argparse.Namespace) -> LanTransferClient:
    password = get_password(args.password, "Enter server password: ")
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
