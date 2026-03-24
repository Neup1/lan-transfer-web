#!/usr/bin/env python3

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
      padding: 64px 18px 28px;
    }
    .page-lang {
      position: fixed;
      top: 14px;
      right: 18px;
      z-index: 10;
      width: 106px;
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
    .password-row {
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .root-row {
      display: grid;
      gap: 8px;
    }
    .root-action-row {
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr 1fr;
      align-items: stretch;
    }
    .root-action-row button {
      width: 100%;
    }
    .field label {
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }
    input[type="password"],
    input[type="text"],
    select {
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
    input[readonly] {
      background: #f6f9ff;
      color: #445e80;
    }
    input[type="password"]:focus,
    input[type="text"]:focus,
    select:focus {
      border-color: #87aaf6;
      box-shadow: 0 0 0 4px #edf3ff;
    }
    select {
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      cursor: pointer;
      background-image:
        linear-gradient(45deg, transparent 50%, #6f83a5 50%),
        linear-gradient(135deg, #6f83a5 50%, transparent 50%);
      background-position:
        calc(100% - 18px) calc(50% - 3px),
        calc(100% - 12px) calc(50% - 3px);
      background-size: 6px 6px, 6px 6px;
      background-repeat: no-repeat;
      padding-right: 34px;
    }
    select:hover {
      border-color: #b7c9e8;
      background-color: #fbfdff;
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
    .lang-toggle {
      width: 100%;
      border-radius: 14px;
      box-shadow: 0 8px 20px rgba(25, 49, 82, 0.12);
      border-color: #c8d6eb;
      background-color: #ffffff;
      color: #2d425d;
      font-weight: 700;
      font-size: 12px;
      padding: 7px 10px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .lang-icon {
      width: 13px;
      height: 13px;
      flex: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .lang-icon img {
      width: 13px;
      height: 13px;
      display: block;
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
    .upload-panel {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      padding: 12px;
      display: grid;
      gap: 10px;
    }
    .transfer-panel {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      padding: 12px;
      display: grid;
      gap: 12px;
    }
    .transfer-panel-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .transfer-panel-head h2 {
      margin: 0;
      font-size: 16px;
      line-height: 1.2;
    }
    .transfer-summary {
      font-size: 12px;
      color: var(--muted);
    }
    .transfer-list {
      display: grid;
      gap: 10px;
    }
    .transfer-empty {
      border: 1px dashed var(--border);
      border-radius: var(--radius-md);
      background: #fbfdff;
      color: var(--muted);
      text-align: center;
      padding: 18px 14px;
      font-size: 13px;
    }
    .transfer-item {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fbfdff;
      padding: 10px;
      display: grid;
      gap: 8px;
    }
    .transfer-top {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: flex-start;
    }
    .transfer-title {
      min-width: 0;
      display: grid;
      gap: 4px;
    }
    .transfer-name {
      font-size: 13px;
      font-weight: 700;
      color: var(--text);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .transfer-subtitle {
      font-size: 12px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .transfer-status-badge {
      flex: none;
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 3px 9px;
      font-size: 11px;
      font-weight: 700;
      background: #fff;
      color: var(--muted);
    }
    .transfer-status-badge.running {
      border-color: #cfe1ff;
      background: #edf4ff;
      color: #2b67bf;
    }
    .transfer-status-badge.paused,
    .transfer-status-badge.queued {
      border-color: #d7dfeb;
      background: #f6f9fd;
      color: #607188;
    }
    .transfer-status-badge.completed {
      border-color: #bfe5ce;
      background: #eefbf3;
      color: #21784b;
    }
    .transfer-status-badge.cancelled,
    .transfer-status-badge.error {
      border-color: #f1b9c3;
      background: #fff2f4;
      color: var(--danger);
    }
    .transfer-progress {
      height: 8px;
      border-radius: 999px;
      background: #e6edf7;
      overflow: hidden;
    }
    .transfer-progress-bar {
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, #2f6fdf 0%, #79a7ff 100%);
      transition: width 0.12s linear;
    }
    .transfer-meta-row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    .transfer-note {
      min-width: 0;
      font-size: 12px;
      color: var(--muted);
      word-break: break-word;
    }
    .transfer-stats {
      flex: none;
      font-size: 12px;
      color: var(--muted);
      white-space: nowrap;
    }
    .transfer-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
      flex-wrap: wrap;
    }
    .transfer-actions button {
      box-shadow: none;
      padding: 8px 12px;
      font-size: 12px;
    }
    .browser-toolbar {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fff;
      padding: 10px;
      display: grid;
      gap: 10px;
    }
    .filter-grid {
      display: grid;
      gap: 10px;
      grid-template-columns: minmax(0, 1fr) 160px 150px minmax(220px, 0.9fr);
      align-items: center;
    }
    .upload-row {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .upload-meta {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .path-actions {
      display: grid;
      gap: 10px;
      grid-template-columns: 1fr auto;
      align-items: center;
    }
    .path-action-buttons {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .file-picker {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #f9fbff;
      min-height: 44px;
      padding: 6px 8px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .file-pick-btn {
      box-shadow: none;
      padding: 8px 12px;
      font-size: 13px;
      white-space: nowrap;
    }
    .file-picked-text {
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }
    .file-input-hidden {
      display: none;
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
    .folder-mini {
      display: grid;
      gap: 8px;
      grid-template-columns: 1fr auto;
      align-items: center;
      grid-column: auto;
      min-width: 0;
      width: 100%;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      background: #fbfdff;
      padding: 6px;
    }
    .folder-mini input {
      min-width: 0;
      padding: 8px 10px;
      font-size: 13px;
      border-radius: 10px;
    }
    .folder-mini button {
      box-shadow: none;
      padding: 8px 12px;
      font-size: 13px;
      white-space: nowrap;
    }
    .drop-zone {
      border: 1px dashed #b7cae7;
      border-radius: var(--radius-md);
      background: #f8fbff;
      color: #4f637d;
      text-align: center;
      padding: 26px 12px;
      min-height: 150px;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    .drop-zone.drag {
      border-color: #6f9ded;
      background: #edf4ff;
      color: #2b67bf;
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
      body { padding-top: 76px; }
      .page-lang {
        right: 12px;
        top: 10px;
        width: 96px;
      }
      .filter-grid { grid-template-columns: 1fr; }
      .upload-row { grid-template-columns: 1fr; }
      .upload-meta { grid-template-columns: 1fr; }
      .path-actions { grid-template-columns: 1fr; }
      .path-action-buttons { width: 100%; }
      .path-action-buttons button { flex: 1; }
      .transfer-top,
      .transfer-meta-row,
      .transfer-actions {
        align-items: stretch;
      }
      .transfer-actions button { flex: 1; }
      .folder-mini {
        min-width: 0;
        width: 100%;
        grid-column: auto;
      }
      th:nth-child(3),
      td:nth-child(3),
      th:nth-child(4),
      td:nth-child(4) { display: none; }
    }
  </style>
</head>
<body>
  <div class="page-lang">
    <button id="langToggleBtn" class="ghost lang-toggle" type="button">
      <span class="lang-icon" aria-hidden="true"><img src="/assets/globe.svg" alt=""></span>
      <span id="langToggleText">中文</span>
    </button>
  </div>
  <div class="shell">
    <aside class="card side">
      <div class="headline">
        <h1>LAN Transfer</h1>
        <p id="headlineDesc">Fast local network file transfer with password authentication.</p>
      </div>
      <div class="field">
        <label id="passwordLabel" for="passwordInput">Password</label>
        <div class="password-row">
          <input id="passwordInput" type="password" placeholder="Enter server passphrase">
          <button id="togglePasswordBtn" class="ghost" type="button">Show</button>
        </div>
      </div>
      <div class="inline">
        <button id="loginBtn">Sign In</button>
        <button id="logoutBtn" class="ghost">Sign Out</button>
      </div>
      <div id="tokenMeta" class="tiny">Token: not issued</div>
      <div id="status" class="status">Not signed in.</div>
      <div class="field">
        <label id="serverTokenLabel" for="serverTokenInput">Server Token</label>
        <div class="password-row">
          <input id="serverTokenInput" type="password" readonly value="******">
          <button id="toggleServerTokenBtn" class="ghost" type="button">Show</button>
        </div>
        <div id="serverTokenHint" class="tiny">Only visible on the server machine.</div>
      </div>
      <div class="field">
        <label id="serverRootLabel" for="serverRootInput">Upload Root</label>
        <div class="root-row">
          <input id="serverRootInput" type="text" placeholder="e.g. D:/LAN_SHARE">
          <div class="root-action-row">
            <button id="serverRootPickBtn" class="ghost" type="button">Browse</button>
            <button id="serverRootApplyBtn" class="soft" type="button">Apply</button>
          </div>
        </div>
        <div id="serverRootHint" class="tiny">Only visible and editable on the server machine.</div>
      </div>
      <div id="tipText" class="tiny">Tip: This page works best when opened from the same host running the server.</div>
    </aside>
    <main class="card main">
      <div class="upload-panel">
        <div class="upload-row">
          <div class="file-picker">
            <button id="filePickBtn" class="ghost file-pick-btn" type="button">Choose Files</button>
            <span id="filePickText" class="file-picked-text">No file selected</span>
            <input id="uploadInput" class="file-input-hidden" type="file" multiple>
          </div>
          <button id="uploadBtn">Upload</button>
        </div>
        <div class="upload-meta">
          <label class="upload-option">
            <input id="resumeCheckbox" type="checkbox" checked>
            <span id="resumeLabelText">Resume if same file already exists</span>
          </label>
        </div>
        <div id="dropZone" class="drop-zone">Drag files here to upload</div>
      </div>

      <div class="transfer-panel">
        <div class="transfer-panel-head">
          <h2 id="transferTitle">Transfers</h2>
          <div id="transferSummary" class="transfer-summary">No active tasks</div>
        </div>
        <div id="transferList" class="transfer-list">
          <div class="transfer-empty">No transfers yet.</div>
        </div>
      </div>

      <div class="browser-toolbar">
        <div class="path-actions">
          <div id="breadcrumbs" class="path-chip"></div>
          <div class="path-action-buttons">
            <button id="refreshBtn" class="soft">Refresh</button>
            <button id="upBtn" class="ghost">Up</button>
          </div>
        </div>
        <div class="filter-grid">
          <input id="searchInput" type="text" placeholder="Search files/folders">
          <select id="sortBySelect">
            <option value="name">Sort: Name</option>
            <option value="size">Sort: Size</option>
            <option value="mtime">Sort: Modified Time</option>
            <option value="type">Sort: Type</option>
          </select>
          <select id="sortOrderSelect">
            <option value="asc">Order: Ascending</option>
            <option value="desc">Order: Descending</option>
          </select>
          <div class="folder-mini">
            <input id="mkdirInput" type="text" placeholder="New folder name">
            <button id="mkdirBtn" class="soft">Create Folder</button>
          </div>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th id="thName" style="width: 44%;">Name</th>
              <th id="thType" style="width: 11%;">Type</th>
              <th id="thSize" style="width: 15%;">Size</th>
              <th id="thModified" style="width: 18%;">Modified</th>
              <th id="thActions" style="width: 12%; text-align: right;">Actions</th>
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
    // 前端运行时状态：会话令牌、当前路径、排序与语言等。
    const tokenKey = "lan_transfer_token";
    const tokenExpKey = "lan_transfer_token_exp";
    const langKey = "lan_transfer_lang";
    const state = {
      token: sessionStorage.getItem(tokenKey) || "",
      tokenExp: Number(sessionStorage.getItem(tokenExpKey) || "0"),
      serverPassphrase: "",
      serverPassphraseAvailable: false,
      showServerPassphrase: false,
      serverRootPath: "",
      serverRootAvailable: false,
      path: "",
      entries: [],
      searchText: "",
      sortBy: "name",
      sortOrder: "asc",
      // 首次访问默认中文。
      lang: localStorage.getItem(langKey) || "zh",
      refreshTimer: null,
      refreshing: false,
      transfers: [],
      transferSeq: 0,
      maxActiveUploads: 1,
      maxActiveDownloads: 1
    };

    const $ = (sel) => document.querySelector(sel);
    const statusEl = $("#status");
    const tokenMetaEl = $("#tokenMeta");
    const transferTitle = $("#transferTitle");
    const transferSummary = $("#transferSummary");
    const transferList = $("#transferList");
    const serverTokenLabel = $("#serverTokenLabel");
    const serverTokenInput = $("#serverTokenInput");
    const serverTokenHint = $("#serverTokenHint");
    const toggleServerTokenBtn = $("#toggleServerTokenBtn");
    const serverRootLabel = $("#serverRootLabel");
    const serverRootInput = $("#serverRootInput");
    const serverRootHint = $("#serverRootHint");
    const serverRootPickBtn = $("#serverRootPickBtn");
    const serverRootApplyBtn = $("#serverRootApplyBtn");
    const passwordInput = $("#passwordInput");
    const togglePasswordBtn = $("#togglePasswordBtn");
    const loginBtn = $("#loginBtn");
    const logoutBtn = $("#logoutBtn");
    const refreshBtn = $("#refreshBtn");
    const upBtn = $("#upBtn");
    const filePickBtn = $("#filePickBtn");
    const filePickText = $("#filePickText");
    const uploadInput = $("#uploadInput");
    const uploadBtn = $("#uploadBtn");
    const mkdirInput = $("#mkdirInput");
    const mkdirBtn = $("#mkdirBtn");
    const resumeCheckbox = $("#resumeCheckbox");
    const breadcrumbs = $("#breadcrumbs");
    const fileBody = $("#fileBody");
    const dropZone = $("#dropZone");
    const searchInput = $("#searchInput");
    const sortBySelect = $("#sortBySelect");
    const sortOrderSelect = $("#sortOrderSelect");
    const langToggleBtn = $("#langToggleBtn");
    const langToggleText = $("#langToggleText");
    const headlineDesc = $("#headlineDesc");
    const passwordLabel = $("#passwordLabel");
    const tipText = $("#tipText");
    const resumeLabelText = $("#resumeLabelText");
    const thName = $("#thName");
    const thType = $("#thType");
    const thSize = $("#thSize");
    const thModified = $("#thModified");
    const thActions = $("#thActions");

    // 多语言字典（英文/中文）。
    const i18n = {
      en: {
        headlineDesc: "Fast local network file transfer with password authentication.",
        transfersTitle: "Transfers",
        transfersEmpty: "No transfers yet.",
        transfersSummaryEmpty: "No active tasks",
        transfersSummary: "{running} running / {queued} queued / {paused} paused",
        transferStatusQueued: "Queued",
        transferStatusRunning: "Running",
        transferStatusPaused: "Paused",
        transferStatusCompleted: "Completed",
        transferStatusCancelled: "Cancelled",
        transferStatusError: "Failed",
        transferPreparing: "Preparing transfer...",
        transferWaitingUpload: "Waiting for another upload to finish.",
        transferWaitingDownload: "Waiting for another download to finish.",
        transferCompletedNote: "Transfer completed.",
        transferCancelledNote: "Transfer cancelled.",
        transferPausedNote: "Transfer paused.",
        transferSkippedExisting: "File already complete, skipped.",
        transfersQueued: "{count} transfer(s) added to the list.",
        uploadTask: "Upload",
        downloadTask: "Download",
        pause: "Pause",
        resume: "Resume",
        cancel: "Cancel",
        remove: "Remove",
        downloadMemoryFallback: "This browser will keep the download in memory until it finishes.",
        downloadPickerCancelled: "Save location selection was cancelled.",
        browserStreamUnsupported: "This browser does not support streamed download control.",
        downloadFailedHttp: "Download failed with HTTP {code}",
        downloadCompletedStatus: "Downloaded: {name}",
        uploadCompletedStatus: "Uploaded: {name}",
        tokenNotIssued: "Token: not issued",
        tokenExpiresAt: "Token expires at: {time}",
        serverTokenLabel: "Server Passphrase",
        serverTokenHintLocal: "Visible only on this server machine.",
        serverTokenHintUnavailable: "Unavailable: open this page on the server machine to view.",
        serverTokenMasked: "******",
        serverRootLabel: "Upload Root Directory",
        serverRootHintLocal: "Only this server machine can view and change the upload root.",
        serverRootHintUnavailable: "Unavailable: open this page on the server machine.",
        serverRootHintNeedSignIn: "Sign in first, then you can change the upload root directory.",
        serverRootPlaceholder: "e.g. D:/LAN_SHARE",
        browseRoot: "Browse",
        applyRoot: "Apply",
        pickRootOpening: "Opening folder picker on server machine...",
        pickRootCancelled: "Folder selection cancelled.",
        enterServerRootFirst: "Please enter a root directory path first.",
        rootUpdated: "Upload root changed to: {root}",
        notSignedIn: "Not signed in.",
        signInToLoad: "Sign in to load files.",
        signedOut: "Signed out.",
        authExpired: "Authentication expired. Please sign in again.",
        enterPassphraseFirst: "Please enter passphrase first.",
        signingIn: "Signing in...",
        signedInLoading: "Signed in. Loading files...",
        noMatch: "No files/folders match current filter.",
        folder: "Folder",
        file: "File",
        open: "Open",
        download: "Download",
        pleaseSignInFirst: "Please sign in first.",
        downloadStarted: "Download started: {path}",
        remoteTargetIsFolder: "Remote target is a folder: {path}",
        networkUploadError: "Network error during upload.",
        uploadFailedHttp: "Upload failed with HTTP {code}",
        chooseFilesFirst: "Choose files first.",
        skippedExisting: "Skipped existing file: {name} ({done}/{total})",
        uploading: "Uploading {name} {pct}% ({done}/{total})",
        uploaded: "Uploaded: {name} ({done}/{total})",
        enterFolderName: "Please enter folder name.",
        folderCreated: "Folder created: {name}",
        refreshed: "Refreshed.",
        sessionRestored: "Session restored.",
        show: "Show",
        hide: "Hide",
        root: "root",
        searchPlaceholder: "Search files/folders",
        sortName: "Sort: Name",
        sortSize: "Sort: Size",
        sortMtime: "Sort: Modified Time",
        sortType: "Sort: Type",
        orderAsc: "Order: Ascending",
        orderDesc: "Order: Descending",
        dropHint: "Drag files here to upload",
        passwordLabel: "Password",
        passphrasePlaceholder: "Enter server passphrase",
        login: "Sign In",
        logout: "Sign Out",
        refresh: "Refresh",
        up: "Up",
        upload: "Upload",
        chooseFilesButton: "Choose Files",
        noFileSelected: "No file selected",
        filesSelected: "{count} files selected",
        createFolder: "Create Folder",
        folderPlaceholder: "New folder name",
        resumeLabel: "Resume if same file already exists",
        tableName: "Name",
        tableType: "Type",
        tableSize: "Size",
        tableModified: "Modified",
        tableActions: "Actions",
        tipText: "Tip: This page works best when opened from the same host running the server."
      },
      zh: {
        headlineDesc: "局域网高速文件传输，支持口令认证。",
        transfersTitle: "传输列表",
        transfersEmpty: "暂无传输任务。",
        transfersSummaryEmpty: "当前没有活动任务",
        transfersSummary: "运行中 {running} / 排队中 {queued} / 已暂停 {paused}",
        transferStatusQueued: "排队中",
        transferStatusRunning: "传输中",
        transferStatusPaused: "已暂停",
        transferStatusCompleted: "已完成",
        transferStatusCancelled: "已取消",
        transferStatusError: "失败",
        transferPreparing: "正在准备传输...",
        transferWaitingUpload: "等待前一个上传任务结束后开始。",
        transferWaitingDownload: "等待前一个下载任务结束后开始。",
        transferCompletedNote: "传输已完成。",
        transferCancelledNote: "传输已取消。",
        transferPausedNote: "传输已暂停。",
        transferSkippedExisting: "文件已完整存在，已跳过。",
        transfersQueued: "已加入 {count} 个传输任务。",
        uploadTask: "上传",
        downloadTask: "下载",
        pause: "暂停",
        resume: "继续",
        cancel: "取消",
        remove: "移除",
        downloadMemoryFallback: "当前浏览器会先把下载内容保存在内存中，完成后再保存。",
        downloadPickerCancelled: "已取消选择保存位置。",
        browserStreamUnsupported: "当前浏览器不支持可控流式下载。",
        downloadFailedHttp: "下载失败，HTTP 状态码：{code}",
        downloadCompletedStatus: "下载完成：{name}",
        uploadCompletedStatus: "上传完成：{name}",
        tokenNotIssued: "令牌：未签发",
        tokenExpiresAt: "令牌到期时间：{time}",
        serverTokenLabel: "服务器通行令牌",
        serverTokenHintLocal: "仅服务器本机可查看。",
        serverTokenHintUnavailable: "不可查看：请在服务器本机打开此页面。",
        serverTokenMasked: "******",
        serverRootLabel: "上传根目录",
        serverRootHintLocal: "仅服务器本机可查看和修改上传根目录。",
        serverRootHintUnavailable: "不可操作：请在服务器本机打开此页面。",
        serverRootHintNeedSignIn: "请先登录，然后可修改上传根目录。",
        serverRootPlaceholder: "例如 D:/LAN_SHARE",
        browseRoot: "选择文件夹",
        applyRoot: "应用",
        pickRootOpening: "正在服务器端打开文件夹选择窗口...",
        pickRootCancelled: "已取消选择文件夹。",
        enterServerRootFirst: "请先输入根目录路径。",
        rootUpdated: "上传根目录已切换为：{root}",
        notSignedIn: "未登录。",
        signInToLoad: "请先登录再加载文件。",
        signedOut: "已退出登录。",
        authExpired: "认证已过期，请重新登录。",
        enterPassphraseFirst: "请先输入通行口令。",
        signingIn: "登录中...",
        signedInLoading: "登录成功，正在加载文件...",
        noMatch: "当前筛选条件下没有匹配的文件或文件夹。",
        folder: "文件夹",
        file: "文件",
        open: "打开",
        download: "下载",
        pleaseSignInFirst: "请先登录。",
        downloadStarted: "已开始下载：{path}",
        remoteTargetIsFolder: "远端目标是文件夹：{path}",
        networkUploadError: "上传过程中出现网络错误。",
        uploadFailedHttp: "上传失败，HTTP 状态码：{code}",
        chooseFilesFirst: "请先选择文件。",
        skippedExisting: "已跳过已有文件：{name}（{done}/{total}）",
        uploading: "上传中 {name} {pct}%（{done}/{total}）",
        uploaded: "上传完成：{name}（{done}/{total}）",
        enterFolderName: "请输入文件夹名称。",
        folderCreated: "已创建文件夹：{name}",
        refreshed: "已刷新。",
        sessionRestored: "会话已恢复。",
        show: "显示",
        hide: "隐藏",
        root: "根目录",
        searchPlaceholder: "搜索文件/文件夹",
        sortName: "排序：名称",
        sortSize: "排序：大小",
        sortMtime: "排序：修改时间",
        sortType: "排序：类型",
        orderAsc: "顺序：升序",
        orderDesc: "顺序：降序",
        dropHint: "拖拽文件到这里即可上传",
        passwordLabel: "通行口令",
        passphrasePlaceholder: "输入服务端通行口令",
        login: "登录",
        logout: "退出",
        refresh: "刷新",
        up: "上级",
        upload: "上传",
        chooseFilesButton: "选择文件",
        noFileSelected: "未选择文件",
        filesSelected: "已选择 {count} 个文件",
        createFolder: "新建文件夹",
        folderPlaceholder: "新建文件夹名称",
        resumeLabel: "如果存在同名文件则断点续传",
        tableName: "名称",
        tableType: "类型",
        tableSize: "大小",
        tableModified: "修改时间",
        tableActions: "操作",
        tipText: "提示：建议在运行服务端的同一主机或同一局域网环境访问。"
      }
    };

    function t(key, vars = {}) {
      const table = i18n[state.lang] || i18n.en;
      let text = table[key] || i18n.en[key] || key;
      for (const [k, v] of Object.entries(vars)) {
        text = text.replaceAll("{" + k + "}", String(v));
      }
      return text;
    }

    function updateServerPassphraseUI() {
      serverTokenLabel.textContent = t("serverTokenLabel");
      if (state.serverPassphraseAvailable && state.serverPassphrase) {
        serverTokenInput.type = state.showServerPassphrase ? "text" : "password";
        serverTokenInput.value = state.serverPassphrase;
        toggleServerTokenBtn.disabled = false;
        toggleServerTokenBtn.textContent = state.showServerPassphrase ? t("hide") : t("show");
        serverTokenHint.textContent = t("serverTokenHintLocal");
      } else {
        serverTokenInput.type = "password";
        serverTokenInput.value = t("serverTokenMasked");
        toggleServerTokenBtn.disabled = true;
        toggleServerTokenBtn.textContent = t("show");
        serverTokenHint.textContent = t("serverTokenHintUnavailable");
      }
    }

    async function refreshServerPassphrase() {
      try {
        const data = await requestJson("/api/server-passphrase", {}, false);
        state.serverPassphrase = typeof data.passphrase === "string" ? data.passphrase : "";
        state.serverPassphraseAvailable = Boolean(state.serverPassphrase);
      } catch (err) {
        state.serverPassphrase = "";
        state.serverPassphraseAvailable = false;
        state.showServerPassphrase = false;
      }
      updateServerPassphraseUI();
    }

    function updateServerRootUI() {
      serverRootLabel.textContent = t("serverRootLabel");
      serverRootInput.placeholder = t("serverRootPlaceholder");
      serverRootPickBtn.textContent = t("browseRoot");
      serverRootApplyBtn.textContent = t("applyRoot");
      if (state.serverRootAvailable && state.serverRootPath) {
        serverRootInput.readOnly = false;
        if (document.activeElement !== serverRootInput) {
          serverRootInput.value = state.serverRootPath;
        }
        serverRootPickBtn.disabled = !state.token;
        serverRootApplyBtn.disabled = !state.token;
        serverRootHint.textContent = state.token
          ? t("serverRootHintLocal")
          : t("serverRootHintNeedSignIn");
        return;
      }
      serverRootInput.readOnly = true;
      serverRootInput.value = "";
      serverRootPickBtn.disabled = true;
      serverRootApplyBtn.disabled = true;
      serverRootHint.textContent = t("serverRootHintUnavailable");
    }

    async function refreshServerRoot() {
      try {
        const data = await requestJson("/api/server-root", {}, false);
        const root = typeof data.root === "string" ? data.root.trim() : "";
        state.serverRootPath = root;
        state.serverRootAvailable = Boolean(root);
      } catch (err) {
        state.serverRootPath = "";
        state.serverRootAvailable = false;
      }
      updateServerRootUI();
    }

    async function applyServerRoot() {
      if (!state.serverRootAvailable) {
        setStatus(t("serverRootHintUnavailable"), "error");
        return;
      }
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      const nextRoot = (serverRootInput.value || "").trim();
      if (!nextRoot) {
        setStatus(t("enterServerRootFirst"), "error");
        return;
      }
      serverRootApplyBtn.disabled = true;
      try {
        const data = await requestJson(
          "/api/server-root",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ root: nextRoot })
          },
          true
        );
        state.serverRootPath = typeof data.root === "string" ? data.root : nextRoot;
        state.serverRootAvailable = Boolean(state.serverRootPath);
        state.path = "";
        updateServerRootUI();
        await loadDir("");
        setStatus(t("rootUpdated", { root: state.serverRootPath }), "ok");
      } catch (err) {
        setStatus(String(err.message || err), "error");
      } finally {
        updateServerRootUI();
      }
    }

    async function pickServerRoot() {
      if (!state.serverRootAvailable) {
        setStatus(t("serverRootHintUnavailable"), "error");
        return;
      }
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      serverRootPickBtn.disabled = true;
      serverRootApplyBtn.disabled = true;
      setStatus(t("pickRootOpening"));
      try {
        const data = await requestJson("/api/server-root/pick", { method: "POST" }, true);
        if (data.cancelled) {
          setStatus(t("pickRootCancelled"));
        } else {
          state.serverRootPath = typeof data.root === "string" ? data.root : state.serverRootPath;
          state.serverRootAvailable = Boolean(state.serverRootPath);
          state.path = "";
          await loadDir("");
          setStatus(t("rootUpdated", { root: state.serverRootPath }), "ok");
        }
      } catch (err) {
        setStatus(String(err.message || err), "error");
      } finally {
        updateServerRootUI();
      }
    }

    function applyLanguage() {
      // 将翻译文案应用到按钮、占位符、表头等可见控件。
      langToggleText.textContent = state.lang === "zh" ? "中文" : "English";
      document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
      headlineDesc.textContent = t("headlineDesc");
      passwordLabel.textContent = t("passwordLabel");
      passwordInput.placeholder = t("passphrasePlaceholder");
      loginBtn.textContent = t("login");
      logoutBtn.textContent = t("logout");
      refreshBtn.textContent = t("refresh");
      upBtn.textContent = t("up");
      filePickBtn.textContent = t("chooseFilesButton");
      uploadBtn.textContent = t("upload");
      mkdirBtn.textContent = t("createFolder");
      mkdirInput.placeholder = t("folderPlaceholder");
      searchInput.placeholder = t("searchPlaceholder");
      sortBySelect.options[0].text = t("sortName");
      sortBySelect.options[1].text = t("sortSize");
      sortBySelect.options[2].text = t("sortMtime");
      sortBySelect.options[3].text = t("sortType");
      sortOrderSelect.options[0].text = t("orderAsc");
      sortOrderSelect.options[1].text = t("orderDesc");
      dropZone.textContent = t("dropHint");
      resumeLabelText.textContent = t("resumeLabel");
      thName.textContent = t("tableName");
      thType.textContent = t("tableType");
      thSize.textContent = t("tableSize");
      thModified.textContent = t("tableModified");
      thActions.textContent = t("tableActions");
      tipText.textContent = t("tipText");
      if (passwordInput.type === "password") {
        togglePasswordBtn.textContent = t("show");
      } else {
        togglePasswordBtn.textContent = t("hide");
      }
      updateServerPassphraseUI();
      updateServerRootUI();
      updateSelectedFileLabel();
      updateTokenMeta();
      renderTransfers();
    }

    function updateSelectedFileLabel() {
      const files = uploadInput.files ? Array.from(uploadInput.files) : [];
      if (!files.length) {
        filePickText.textContent = t("noFileSelected");
        return;
      }
      if (files.length === 1) {
        filePickText.textContent = files[0].name;
        return;
      }
      filePickText.textContent = t("filesSelected", { count: files.length });
    }

    function nextTransferId() {
      state.transferSeq += 1;
      return "transfer-" + state.transferSeq;
    }

    function createTransferTask(data) {
      const task = {
        id: nextTransferId(),
        kind: data.kind || "upload",
        name: data.name || "",
        remotePath: data.remotePath || "",
        totalBytes: Number(data.totalBytes || 0),
        transferredBytes: Number(data.transferredBytes || 0),
        status: "queued",
        noteKey: data.noteKey || "transferPreparing",
        noteVars: data.noteVars || {},
        errorText: "",
        speed: 0,
        allowResume: data.allowResume !== false,
        file: data.file || null,
        fileHandle: data.fileHandle || null,
        storage: data.storage || "",
        memoryChunks: Array.isArray(data.memoryChunks) ? data.memoryChunks : [],
        objectUrl: "",
        xhr: null,
        controller: null,
        abortReason: "",
        writable: null,
        startedAt: 0
      };
      state.transfers.unshift(task);
      renderTransfers();
      scheduleTransfers();
      return task;
    }

    function getTransferById(id) {
      return state.transfers.find((task) => task.id === id) || null;
    }

    function transferStatusKey(status) {
      if (status === "running") return "transferStatusRunning";
      if (status === "paused") return "transferStatusPaused";
      if (status === "completed") return "transferStatusCompleted";
      if (status === "cancelled") return "transferStatusCancelled";
      if (status === "error") return "transferStatusError";
      return "transferStatusQueued";
    }

    function transferStatusText(task) {
      return t(transferStatusKey(task.status));
    }

    function transferKindText(task) {
      return task.kind === "download" ? t("downloadTask") : t("uploadTask");
    }

    function transferNoteText(task) {
      if (task.errorText) return task.errorText;
      if (task.noteKey) return t(task.noteKey, task.noteVars || {});
      return transferStatusText(task);
    }

    function transferPercent(task) {
      if (!task.totalBytes) return 0;
      return Math.max(0, Math.min(100, (Number(task.transferredBytes || 0) * 100) / task.totalBytes));
    }

    function runningTransferCount(kind) {
      return state.transfers.filter((task) => task.kind === kind && task.status === "running").length;
    }

    function setTaskNote(task, noteKey = "", noteVars = {}, errorText = "") {
      task.noteKey = noteKey;
      task.noteVars = noteVars || {};
      task.errorText = errorText || "";
    }

    function clearTaskRuntime(task) {
      task.abortReason = "";
      task.speed = 0;
      task.startedAt = 0;
      task.xhr = null;
      task.controller = null;
      task.writable = null;
    }

    function countChunkBytes(chunks) {
      return (chunks || []).reduce((sum, chunk) => sum + Number(chunk && chunk.byteLength ? chunk.byteLength : 0), 0);
    }

    function renderTransfers() {
      transferTitle.textContent = t("transfersTitle");
      if (!state.transfers.length) {
        transferSummary.textContent = t("transfersSummaryEmpty");
        transferList.innerHTML = "";
        const empty = document.createElement("div");
        empty.className = "transfer-empty";
        empty.textContent = t("transfersEmpty");
        transferList.appendChild(empty);
        return;
      }

      const running = state.transfers.filter((task) => task.status === "running").length;
      const queued = state.transfers.filter((task) => task.status === "queued").length;
      const paused = state.transfers.filter((task) => task.status === "paused").length;
      transferSummary.textContent = t("transfersSummary", { running, queued, paused });

      transferList.innerHTML = "";
      for (const task of state.transfers) {
        const item = document.createElement("div");
        item.className = "transfer-item";

        const top = document.createElement("div");
        top.className = "transfer-top";

        const title = document.createElement("div");
        title.className = "transfer-title";

        const name = document.createElement("div");
        name.className = "transfer-name";
        name.textContent = task.name || task.remotePath || transferKindText(task);
        title.appendChild(name);

        const subtitle = document.createElement("div");
        subtitle.className = "transfer-subtitle";
        subtitle.textContent = transferKindText(task) + " · " + (task.remotePath || task.name || "-");
        title.appendChild(subtitle);
        top.appendChild(title);

        const badge = document.createElement("div");
        badge.className = "transfer-status-badge " + task.status;
        badge.textContent = transferStatusText(task);
        top.appendChild(badge);
        item.appendChild(top);

        const progressWrap = document.createElement("div");
        progressWrap.className = "transfer-progress";
        const progressBar = document.createElement("div");
        progressBar.className = "transfer-progress-bar";
        progressBar.style.width = transferPercent(task).toFixed(2) + "%";
        progressWrap.appendChild(progressBar);
        item.appendChild(progressWrap);

        const metaRow = document.createElement("div");
        metaRow.className = "transfer-meta-row";

        const note = document.createElement("div");
        note.className = "transfer-note";
        note.textContent = transferNoteText(task);
        metaRow.appendChild(note);

        const stats = document.createElement("div");
        stats.className = "transfer-stats";
        const bytesText = formatBytes(task.transferredBytes || 0) + " / " + formatBytes(task.totalBytes || 0);
        if (task.status === "running" && task.speed > 0) {
          stats.textContent = bytesText + " · " + formatBytes(task.speed) + "/s";
        } else {
          stats.textContent = bytesText;
        }
        metaRow.appendChild(stats);
        item.appendChild(metaRow);

        const actions = document.createElement("div");
        actions.className = "transfer-actions";

        if (task.status === "running") {
          const pauseBtn = document.createElement("button");
          pauseBtn.className = "ghost";
          pauseBtn.type = "button";
          pauseBtn.textContent = t("pause");
          pauseBtn.addEventListener("click", () => pauseTransfer(task.id));
          actions.appendChild(pauseBtn);

          const cancelBtn = document.createElement("button");
          cancelBtn.className = "ghost";
          cancelBtn.type = "button";
          cancelBtn.textContent = t("cancel");
          cancelBtn.addEventListener("click", () => cancelTransfer(task.id));
          actions.appendChild(cancelBtn);
        } else if (task.status === "queued") {
          const cancelBtn = document.createElement("button");
          cancelBtn.className = "ghost";
          cancelBtn.type = "button";
          cancelBtn.textContent = t("cancel");
          cancelBtn.addEventListener("click", () => cancelTransfer(task.id));
          actions.appendChild(cancelBtn);
        } else if (task.status === "paused" || task.status === "error") {
          const resumeBtn = document.createElement("button");
          resumeBtn.className = "soft";
          resumeBtn.type = "button";
          resumeBtn.textContent = t("resume");
          resumeBtn.addEventListener("click", () => resumeTransfer(task.id));
          actions.appendChild(resumeBtn);

          const cancelBtn = document.createElement("button");
          cancelBtn.className = "ghost";
          cancelBtn.type = "button";
          cancelBtn.textContent = t("cancel");
          cancelBtn.addEventListener("click", () => cancelTransfer(task.id));
          actions.appendChild(cancelBtn);
        } else {
          const removeBtn = document.createElement("button");
          removeBtn.className = "ghost";
          removeBtn.type = "button";
          removeBtn.textContent = t("remove");
          removeBtn.addEventListener("click", () => removeTransfer(task.id));
          actions.appendChild(removeBtn);
        }

        item.appendChild(actions);
        transferList.appendChild(item);
      }
    }

    function setStatus(text, kind = "") {
      statusEl.textContent = text;
      statusEl.className = "status" + (kind ? " " + kind : "");
    }

    function updateTokenMeta() {
      if (!state.token || !state.tokenExp) {
        tokenMetaEl.textContent = t("tokenNotIssued");
        return;
      }
      tokenMetaEl.textContent = t("tokenExpiresAt", {
        time: new Date(state.tokenExp).toLocaleString()
      });
    }

    function parseTokenExpiryFromPayload(token) {
      try {
        const payload = token.split(".")[0];
        const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
        const padding = "=".repeat((4 - (normalized.length % 4)) % 4);
        const binary = atob(normalized + padding);
        const bytes = Uint8Array.from(binary, (ch) => ch.charCodeAt(0));
        const text = new TextDecoder().decode(bytes);
        const parsed = JSON.parse(text);
        if (parsed.exp) {
          return Number(parsed.exp) * 1000;
        }
      } catch (ignore) {
      }
      return 0;
    }

    function setToken(token, expiresInSeconds = 0) {
      state.token = token || "";
      if (!state.token) {
        state.tokenExp = 0;
        sessionStorage.removeItem(tokenKey);
        sessionStorage.removeItem(tokenExpKey);
        updateTokenMeta();
        updateServerRootUI();
        return;
      }
      if (expiresInSeconds > 0) {
        state.tokenExp = Date.now() + Number(expiresInSeconds) * 1000;
      } else {
        state.tokenExp = parseTokenExpiryFromPayload(state.token);
      }
      sessionStorage.setItem(tokenKey, state.token);
      sessionStorage.setItem(tokenExpKey, String(state.tokenExp || 0));
      updateTokenMeta();
      updateServerRootUI();
      ensureRefreshTimer();
    }

    function clearSession() {
      setToken("");
      clearTable(t("signInToLoad"));
      setStatus(t("signedOut"));
      updateServerRootUI();
    }

    function scheduleTransfers() {
      const uploadSlots = Math.max(1, Number(state.maxActiveUploads || 1));
      const downloadSlots = Math.max(1, Number(state.maxActiveDownloads || 1));

      let runningUploads = runningTransferCount("upload");
      let runningDownloads = runningTransferCount("download");

      for (const task of state.transfers) {
        if (task.status !== "queued") continue;
        if (task.kind === "upload") {
          if (runningUploads >= uploadSlots) {
            setTaskNote(task, "transferWaitingUpload");
            continue;
          }
          runningUploads += 1;
          startUploadTask(task);
        } else {
          if (runningDownloads >= downloadSlots) {
            setTaskNote(task, "transferWaitingDownload");
            continue;
          }
          runningDownloads += 1;
          startDownloadTask(task);
        }
      }

      renderTransfers();
    }

    async function safeRefreshDir() {
      if (!state.token) return;
      try {
        await loadDir(state.path || "");
      } catch (err) {
      }
    }

    async function fetchRemoteFileSize(remotePath) {
      const stat = await requestJson("/api/stat?path=" + encodeURIComponent(remotePath));
      if (!stat.exists || stat.is_dir) return 0;
      return Number(stat.size || 0);
    }

    async function syncUploadTaskProgress(task) {
      try {
        task.transferredBytes = await fetchRemoteFileSize(task.remotePath);
      } catch (err) {
      }
      task.totalBytes = task.file ? task.file.size : task.totalBytes;
    }

    async function syncDownloadTaskProgress(task) {
      if (task.fileHandle) {
        try {
          const file = await task.fileHandle.getFile();
          task.transferredBytes = Number(file.size || 0);
          return;
        } catch (err) {
        }
      }
      task.transferredBytes = countChunkBytes(task.memoryChunks);
    }

    async function finishTaskAbort(task, status, noteKey, syncProgress) {
      clearTaskRuntime(task);
      if (syncProgress) {
        await syncProgress(task);
      }
      task.status = status;
      setTaskNote(task, noteKey);
      renderTransfers();
      scheduleTransfers();
    }

    async function failTask(task, err) {
      clearTaskRuntime(task);
      task.status = "error";
      setTaskNote(task, "", {}, String((err && err.message) || err || "Unknown error"));
      renderTransfers();
      scheduleTransfers();
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
      rootBtn.textContent = t("root");
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

    async function requestJson(path, options = {}, auth = true) {
      const headers = new Headers(options.headers || {});
      headers.set("Accept", "application/json");
      if (auth && state.token) {
        headers.set("Authorization", "Bearer " + state.token);
      }
      const response = await fetch(path, { ...options, headers });
      if (response.status === 401) {
        setToken("");
        throw new Error(t("authExpired"));
      }
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || ("HTTP " + response.status));
      }
      return data;
    }

    async function refreshToken(force = false) {
      if (!state.token || state.refreshing) return;
      if (!force && state.tokenExp && (state.tokenExp - Date.now()) > 5 * 60 * 1000) return;
      state.refreshing = true;
      try {
        const data = await requestJson("/api/refresh", { method: "POST" }, true);
        setToken(data.token || "", Number(data.expires_in || 0));
      } catch (err) {
        clearSession();
        setStatus(String(err.message || err), "error");
      } finally {
        state.refreshing = false;
      }
    }

    function ensureRefreshTimer() {
      if (state.refreshTimer) return;
      state.refreshTimer = setInterval(() => {
        refreshToken(false);
      }, 30000);
    }

    async function signIn() {
      const password = passwordInput.value;
      if (!password) {
        setStatus(t("enterPassphraseFirst"), "error");
        return;
      }
      loginBtn.disabled = true;
      try {
        setStatus(t("signingIn"));
        const login = await requestJson(
          "/api/login",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password })
          },
          false
        );
        setToken(login.token || "", Number(login.expires_in || 0));
        passwordInput.value = "";
        setStatus(t("signedInLoading"), "ok");
        await loadDir(state.path || "");
      } catch (err) {
        setStatus(String(err.message || err), "error");
      } finally {
        loginBtn.disabled = false;
      }
    }

    async function loadDir(path) {
      if (!state.token) {
        clearTable(t("signInToLoad"));
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

    function entryValue(item, key) {
      if (key === "size") return Number(item.size || 0);
      if (key === "mtime") return Number(item.mtime || 0);
      if (key === "type") return item.type || "";
      return (item.name || "").toLowerCase();
    }

    function compareEntries(a, b) {
      const dirDelta = (a.type === "dir" ? -1 : 1) - (b.type === "dir" ? -1 : 1);
      if (state.sortBy !== "type" && dirDelta !== 0) return dirDelta;
      const av = entryValue(a, state.sortBy);
      const bv = entryValue(b, state.sortBy);
      let cmp = 0;
      if (typeof av === "number" && typeof bv === "number") cmp = av - bv;
      else cmp = String(av).localeCompare(String(bv));
      if (cmp === 0) cmp = String(a.name || "").localeCompare(String(b.name || ""));
      return state.sortOrder === "asc" ? cmp : -cmp;
    }

    function filteredEntries() {
      const keyword = (state.searchText || "").trim().toLowerCase();
      const rows = state.entries.filter((item) => {
        if (!keyword) return true;
        return String(item.name || "").toLowerCase().includes(keyword);
      });
      rows.sort(compareEntries);
      return rows;
    }

    function renderFiles() {
      const rows = filteredEntries();
      if (!rows.length) {
        clearTable(t("noMatch"));
        return;
      }
      fileBody.innerHTML = "";
      for (const item of rows) {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        nameCell.className = "name-cell";
        nameCell.textContent = item.name || "";
        row.appendChild(nameCell);

        const typeCell = document.createElement("td");
        const typePill = document.createElement("span");
        typePill.className = "type-pill " + (item.type === "dir" ? "dir" : "");
        typePill.textContent = item.type === "dir" ? t("folder") : t("file");
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
          openBtn.textContent = t("open");
          openBtn.addEventListener("click", () => {
            loadDir(item.path || "");
          });
          actionCell.appendChild(openBtn);
        } else {
          const downloadBtn = document.createElement("button");
          downloadBtn.className = "ghost";
          downloadBtn.textContent = t("download");
          downloadBtn.addEventListener("click", () => triggerDownload(item.path || "", item.name || "download"));
          actionCell.appendChild(downloadBtn);
        }
        row.appendChild(actionCell);

        fileBody.appendChild(row);
      }
    }

    function triggerDownload(remotePath, fileName) {
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      queueDownload({
        path: remotePath,
        name: fileName || "download"
      });
    }

    async function queryRemoteOffset(remotePath, fileSize, allowResume) {
      const stat = await requestJson("/api/stat?path=" + encodeURIComponent(remotePath));
      if (!stat.exists) return 0;
      if (stat.is_dir) throw new Error(t("remoteTargetIsFolder", { path: remotePath }));
      const remoteSize = Number(stat.size || 0);
      if (!allowResume) return 0;
      if (remoteSize === fileSize) return fileSize;
      if (remoteSize > 0 && remoteSize < fileSize) return remoteSize;
      return 0;
    }

    function uploadTransferChunk(task, offset) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        task.xhr = xhr;
        task.startedAt = Date.now();
        xhr.open("POST", "/api/upload?path=" + encodeURIComponent(task.remotePath), true);
        xhr.setRequestHeader("Authorization", "Bearer " + state.token);
        xhr.setRequestHeader("X-Offset", String(offset));
        xhr.setRequestHeader("Content-Type", "application/octet-stream");

        xhr.upload.onprogress = (event) => {
          if (!event.lengthComputable) return;
          const elapsed = Math.max((Date.now() - task.startedAt) / 1000, 0.001);
          task.transferredBytes = offset + event.loaded;
          task.totalBytes = task.file ? task.file.size : task.totalBytes;
          task.speed = event.loaded / elapsed;
          renderTransfers();
        };

        xhr.onerror = () => {
          task.xhr = null;
          reject(new Error(t("networkUploadError")));
        };
        xhr.onabort = () => {
          task.xhr = null;
          reject(new Error(task.abortReason === "paused" ? "__PAUSED__" : "__CANCELLED__"));
        };
        xhr.onload = () => {
          task.xhr = null;
          if (xhr.status === 401) {
            setToken("");
            reject(new Error(t("authExpired")));
            return;
          }
          if (xhr.status < 200 || xhr.status >= 300) {
            let msg = t("uploadFailedHttp", { code: xhr.status });
            try {
              const payload = JSON.parse(xhr.responseText || "{}");
              if (payload.error) msg = payload.error;
            } catch (ignore) {
            }
            reject(new Error(msg));
            return;
          }
          if (task.file) task.transferredBytes = task.file.size;
          resolve();
        };

        const payload = offset > 0 ? task.file.slice(offset) : task.file;
        xhr.send(payload);
      });
    }

    async function startUploadTask(task) {
      if (!task.file || task.status === "running") return;
      if (!state.token) {
        await failTask(task, new Error(t("pleaseSignInFirst")));
        return;
      }
      task.status = "running";
      task.errorText = "";
      task.abortReason = "";
      setTaskNote(task, "transferPreparing");
      renderTransfers();
      try {
        const offset = await queryRemoteOffset(task.remotePath, task.file.size, task.allowResume);
        task.totalBytes = task.file.size;
        task.transferredBytes = offset;
        if (offset >= task.file.size) {
          clearTaskRuntime(task);
          task.status = "completed";
          setTaskNote(task, "transferSkippedExisting");
          renderTransfers();
          scheduleTransfers();
          await safeRefreshDir();
          return;
        }
        await uploadTransferChunk(task, offset);
        clearTaskRuntime(task);
        task.status = "completed";
        task.transferredBytes = task.file.size;
        setTaskNote(task, "transferCompletedNote");
        renderTransfers();
        scheduleTransfers();
        setStatus(t("uploadCompletedStatus", { name: task.name }), "ok");
        await safeRefreshDir();
      } catch (err) {
        if (err && err.message === "__PAUSED__") {
          await finishTaskAbort(task, "paused", "transferPausedNote", syncUploadTaskProgress);
          return;
        }
        if (err && err.message === "__CANCELLED__") {
          await finishTaskAbort(task, "cancelled", "transferCancelledNote", syncUploadTaskProgress);
          return;
        }
        await failTask(task, err);
      }
    }

    function finalizeMemoryDownload(task) {
      if (task.objectUrl) {
        URL.revokeObjectURL(task.objectUrl);
        task.objectUrl = "";
      }
      const blob = new Blob(task.memoryChunks || [], { type: "application/octet-stream" });
      task.objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = task.objectUrl;
      link.download = task.name || "download";
      document.body.appendChild(link);
      link.click();
      link.remove();
      task.memoryChunks = [];
    }

    async function startDownloadTask(task) {
      if (task.status === "running") return;
      if (!state.token) {
        await failTask(task, new Error(t("pleaseSignInFirst")));
        return;
      }
      task.status = "running";
      task.errorText = "";
      task.abortReason = "";
      setTaskNote(task, "transferPreparing");
      renderTransfers();

      let writable = null;
      try {
        let offset = 0;
        if (task.fileHandle) {
          const existing = await task.fileHandle.getFile();
          offset = task.allowResume ? Number(existing.size || 0) : 0;
        } else {
          offset = task.allowResume ? countChunkBytes(task.memoryChunks) : 0;
        }
        task.transferredBytes = offset;

        task.controller = new AbortController();
        task.startedAt = Date.now();
        const response = await fetch(
          "/api/download?path=" + encodeURIComponent(task.remotePath) + "&offset=" + offset,
          {
            headers: {
              "Authorization": "Bearer " + state.token,
              "Accept": "application/octet-stream"
            },
            signal: task.controller.signal
          }
        );
        if (response.status === 401) {
          setToken("");
          throw new Error(t("authExpired"));
        }
        if (!response.ok) {
          let msg = t("downloadFailedHttp", { code: response.status });
          const payload = await response.json().catch(() => ({}));
          if (payload && payload.error) msg = payload.error;
          throw new Error(msg);
        }

        const totalSize = Number(response.headers.get("X-File-Size") || task.totalBytes || 0);
        task.totalBytes = totalSize;
        if (offset >= totalSize && totalSize > 0) {
          clearTaskRuntime(task);
          task.status = "completed";
          setTaskNote(task, "transferSkippedExisting");
          renderTransfers();
          scheduleTransfers();
          return;
        }

        const reader = response.body && response.body.getReader ? response.body.getReader() : null;
        if (!reader) throw new Error(t("browserStreamUnsupported"));

        if (task.fileHandle) {
          writable = offset > 0
            ? await task.fileHandle.createWritable({ keepExistingData: true })
            : await task.fileHandle.createWritable();
          task.writable = writable;
        } else if (!Array.isArray(task.memoryChunks)) {
          task.memoryChunks = [];
        }

        let moved = 0;
        while (true) {
          const result = await reader.read();
          if (result.done) break;
          const chunk = result.value;
          if (!chunk || !chunk.byteLength) continue;
          if (writable) {
            await writable.write({ type: "write", position: offset + moved, data: chunk });
          } else {
            task.memoryChunks.push(chunk.slice ? chunk.slice(0) : chunk);
          }
          moved += chunk.byteLength;
          const elapsed = Math.max((Date.now() - task.startedAt) / 1000, 0.001);
          task.transferredBytes = offset + moved;
          task.speed = moved / elapsed;
          renderTransfers();
        }

        if (writable) {
          await writable.close();
          task.writable = null;
        }

        clearTaskRuntime(task);
        task.status = "completed";
        task.transferredBytes = totalSize || task.transferredBytes;
        setTaskNote(task, "transferCompletedNote");
        if (!task.fileHandle) {
          finalizeMemoryDownload(task);
        }
        renderTransfers();
        scheduleTransfers();
        setStatus(t("downloadCompletedStatus", { name: task.name }), "ok");
      } catch (err) {
        if (writable) {
          try {
            await writable.close();
          } catch (closeErr) {
          }
          task.writable = null;
        }
        if (err && err.message === "__CANCELLED__") {
          await finishTaskAbort(task, "cancelled", "transferCancelledNote", syncDownloadTaskProgress);
          return;
        }
        if (task.abortReason === "cancelled") {
          await finishTaskAbort(task, "cancelled", "transferCancelledNote", syncDownloadTaskProgress);
          return;
        }
        if (err && (err.name === "AbortError" || err.message === "__PAUSED__")) {
          await finishTaskAbort(task, "paused", "transferPausedNote", syncDownloadTaskProgress);
          return;
        }
        if (task.abortReason === "paused") {
          await finishTaskAbort(task, "paused", "transferPausedNote", syncDownloadTaskProgress);
          return;
        }
        await failTask(task, err);
      }
    }

    async function uploadFiles(files) {
      const list = Array.from(files || []).filter((f) => f && f.name);
      if (!list.length) {
        setStatus(t("chooseFilesFirst"), "error");
        return;
      }
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      for (const file of list) {
        createTransferTask({
          kind: "upload",
          name: file.name,
          remotePath: joinPath(state.path, file.name),
          totalBytes: file.size,
          allowResume: Boolean(resumeCheckbox.checked),
          file: file,
          noteKey: "transferPreparing"
        });
      }
      uploadInput.value = "";
      updateSelectedFileLabel();
      setStatus(t("transfersQueued", { count: list.length }), "ok");
    }

    async function prepareDownloadTarget(fileName) {
      if (typeof window.showSaveFilePicker === "function") {
        try {
          const handle = await window.showSaveFilePicker({
            suggestedName: fileName || "download"
          });
          return { fileHandle: handle, storage: "file-system" };
        } catch (err) {
          if (err && err.name === "AbortError") return null;
          throw err;
        }
      }
      return { fileHandle: null, storage: "memory" };
    }

    async function queueDownload(item) {
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      try {
        const target = await prepareDownloadTarget(item.name || "download");
        if (!target) {
          setStatus(t("downloadPickerCancelled"));
          return;
        }
        createTransferTask({
          kind: "download",
          name: item.name || "download",
          remotePath: item.path || "",
          totalBytes: Number(item.size || 0),
          allowResume: true,
          fileHandle: target.fileHandle,
          storage: target.storage,
          noteKey: target.storage === "memory" ? "downloadMemoryFallback" : "transferPreparing"
        });
        if (target.storage === "memory") {
          setStatus(t("downloadMemoryFallback"), "ok");
        } else {
          setStatus(t("downloadStarted", { path: item.path || item.name || "" }), "ok");
        }
      } catch (err) {
        setStatus(String(err.message || err), "error");
      }
    }

    function pauseTransfer(id) {
      const task = getTransferById(id);
      if (!task || task.status !== "running") return;
      task.abortReason = "paused";
      if (task.xhr) {
        task.xhr.abort();
        return;
      }
      if (task.controller) {
        task.controller.abort();
      }
    }

    function cancelTransfer(id) {
      const task = getTransferById(id);
      if (!task) return;
      if (task.status === "running") {
        task.abortReason = "cancelled";
        if (task.xhr) {
          task.xhr.abort();
          return;
        }
        if (task.controller) {
          task.controller.abort();
          return;
        }
      }
      if (task.status === "queued" || task.status === "paused" || task.status === "error") {
        clearTaskRuntime(task);
        task.status = "cancelled";
        setTaskNote(task, "transferCancelledNote");
        renderTransfers();
        scheduleTransfers();
      }
    }

    function resumeTransfer(id) {
      const task = getTransferById(id);
      if (!task || (task.status !== "paused" && task.status !== "error")) return;
      clearTaskRuntime(task);
      task.status = "queued";
      setTaskNote(task, task.kind === "download" ? "transferWaitingDownload" : "transferWaitingUpload");
      renderTransfers();
      scheduleTransfers();
    }

    function removeTransfer(id) {
      const index = state.transfers.findIndex((task) => task.id === id);
      if (index < 0) return;
      const [task] = state.transfers.splice(index, 1);
      if (task.objectUrl) {
        URL.revokeObjectURL(task.objectUrl);
      }
      renderTransfers();
      scheduleTransfers();
    }

    async function createFolder() {
      const name = (mkdirInput.value || "").trim();
      if (!name) {
        setStatus(t("enterFolderName"), "error");
        return;
      }
      if (!state.token) {
        setStatus(t("pleaseSignInFirst"), "error");
        return;
      }
      try {
        const remotePath = joinPath(state.path, name);
        await requestJson("/api/mkdir?path=" + encodeURIComponent(remotePath), { method: "POST" });
        mkdirInput.value = "";
        setStatus(t("folderCreated", { name: name }), "ok");
        await loadDir(state.path);
      } catch (err) {
        setStatus(String(err.message || err), "error");
      }
    }

    function handleDropEvent(event) {
      event.preventDefault();
      dropZone.classList.remove("drag");
      if (!event.dataTransfer || !event.dataTransfer.files) return;
      uploadFiles(event.dataTransfer.files);
    }

    loginBtn.addEventListener("click", signIn);
    logoutBtn.addEventListener("click", clearSession);
    refreshBtn.addEventListener("click", async () => {
      try {
        await loadDir(state.path);
        setStatus(t("refreshed"), "ok");
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
    uploadBtn.addEventListener("click", () => uploadFiles(uploadInput.files));
    filePickBtn.addEventListener("click", () => {
      uploadInput.click();
    });
    uploadInput.addEventListener("change", () => {
      updateSelectedFileLabel();
    });
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
    togglePasswordBtn.addEventListener("click", () => {
      // 切换口令显示/隐藏，不改变实际输入值。
      if (passwordInput.type === "password") {
        passwordInput.type = "text";
        togglePasswordBtn.textContent = t("hide");
      } else {
        passwordInput.type = "password";
        togglePasswordBtn.textContent = t("show");
      }
    });
    toggleServerTokenBtn.addEventListener("click", () => {
      if (!state.serverPassphraseAvailable) return;
      state.showServerPassphrase = !state.showServerPassphrase;
      updateServerPassphraseUI();
    });
    serverRootPickBtn.addEventListener("click", pickServerRoot);
    serverRootApplyBtn.addEventListener("click", applyServerRoot);
    serverRootInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        applyServerRoot();
      }
    });
    langToggleBtn.addEventListener("click", () => {
      // 单按钮切换中英文，按钮文本显示当前语言。
      const nextLang = state.lang === "zh" ? "en" : "zh";
      state.lang = nextLang;
      localStorage.setItem(langKey, nextLang);
      applyLanguage();
      if (!state.token) {
        clearTable(t("signInToLoad"));
        setStatus(t("notSignedIn"));
      } else {
        renderFiles();
      }
    });
    searchInput.addEventListener("input", () => {
      state.searchText = searchInput.value || "";
      renderFiles();
    });
    sortBySelect.addEventListener("change", () => {
      // 排序字段变化后，立即重排当前文件列表。
      state.sortBy = sortBySelect.value || "name";
      renderFiles();
    });
    sortOrderSelect.addEventListener("change", () => {
      // 排序方向变化后，立即重排当前文件列表。
      state.sortOrder = sortOrderSelect.value || "asc";
      renderFiles();
    });
    dropZone.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropZone.classList.add("drag");
    });
    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("drag");
    });
    dropZone.addEventListener("drop", handleDropEvent);

    (async () => {
      renderBreadcrumbs();
      applyLanguage();
      updateTokenMeta();
      ensureRefreshTimer();
      await refreshServerPassphrase();
      await refreshServerRoot();
      setInterval(refreshServerPassphrase, 10000);
      setInterval(refreshServerRoot, 10000);
      if (!state.token) {
        clearTable(t("signInToLoad"));
        setStatus(t("notSignedIn"));
        return;
      }
      try {
        await refreshToken(true);
        await loadDir("");
        setStatus(t("sessionRestored"), "ok");
      } catch (err) {
        setToken("");
        clearTable(t("signInToLoad"));
        setStatus(String(err.message || err), "error");
      }
    })();
  </script>
</body>
</html>
"""

